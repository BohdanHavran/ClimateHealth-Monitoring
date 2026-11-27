"""Offline source contracts; these tests do not execute Terraform or contact AWS."""
import json
from pathlib import Path
import re
import secrets
import unittest

from scripts.audit_terraform import blocks, build

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'infrastructure/terraform'


class TerraformVariantBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build(BASE)
        cls.variables = {b['labels'][0]: b for b in cls.graph['blocks'] if b['kind']=='variable' and b['scope']=='root'}
        body = cls.variables['origin_verification_header']['body']
        match = re.search(r'regex\(("[^"\n]+"),\s*var\.origin_verification_header', body)
        cls.header_pattern = json.loads(match[1])

    def test_header_rule_remains_linked_to_sensitive_public_input(self):
        var = self.variables['origin_verification_header']
        self.assertEqual(var['attrs']['sensitive'], 'true')
        self.assertIn('== null ? !var.deploy_application', var['body'])
        self.assertEqual(self.header_pattern, '^[A-Za-z0-9_-]{32,128}$')

    def test_header_rejects_wildcards(self):
        for value in ['*'*32, 'a'*31+'*', 'a'*31+'?']:
            self.assertFalse(bool(re.fullmatch(self.header_pattern, value)))

    def test_header_rejects_empty_short_and_over_limit(self):
        for length in [0, 1, 31, 129, 256]:
            self.assertFalse(bool(re.fullmatch(self.header_pattern, 'a'*length)))

    def test_header_rejects_whitespace_controls_and_non_url_safe_chars(self):
        for char in [' ', '\n', '\r', '\t', '\x00', '+', '/', '=', 'é']:
            self.assertFalse(bool(re.fullmatch(self.header_pattern, 'a'*31+char)))

    def test_header_accepts_generated_urlsafe_value_and_boundaries(self):
        self.assertTrue(bool(re.fullmatch(self.header_pattern, secrets.token_urlsafe(48))))
        for length in [32, 128]:
            self.assertTrue(bool(re.fullmatch(self.header_pattern, 'a'*length)))

    def test_hostname_regex_is_correctly_hcl_escaped(self):
        body=self.variables['origin_hostname']['body']
        match=re.search(r'regex\(("(?:\\.|[^"\\])*"),\s*var\.origin_hostname',body)
        pattern=json.loads(match[1])
        self.assertTrue(bool(re.fullmatch(pattern, 'api.example.invalid')))
        self.assertFalse(bool(re.fullmatch(pattern, 'api\\example.invalid')))

    def test_environment_and_region_are_constrained(self):
        self.assertIn('contains(["dev", "production"], var.environment)', self.variables['environment']['body'])
        self.assertIn('var.aws_region == "eu-north-1"', self.variables['aws_region']['body'])
        self.assertNotIn('name_suffix', self.variables)

    def test_one_small_root_without_speculative_ai_or_creation_flags(self):
        self.assertEqual(len(self.variables), 14)
        self.assertEqual({name for name,b in self.variables.items() if 'default' not in b['attrs']}, {'environment','aws_region'})
        self.assertFalse(any(n.endswith('_provisioned') or n.endswith('_reviewed') for n in self.variables))
        self.assertFalse({'owner','aws_account_id','ai','database_mode','mysql_ami_id'} & self.variables.keys())
        all_tf='\n'.join(p.read_text(encoding='utf8') for p in BASE.rglob('*.tf'))
        self.assertNotIn('moved {', all_tf)
        self.assertNotIn('aws_ec2_instance_state', all_tf)
        self.assertNotIn('resource "aws_instance"', all_tf)
        self.assertNotIn('terraform_remote_state', all_tf)
        self.assertNotIn('review_gate', all_tf)

    def test_data_and_logs_are_not_destroyed_by_application_gate(self):
        root=blocks(BASE/'main.tf',BASE)
        for name in ['networking','ecr','frontend','database']:
            call=next(b for b in root if b['kind']=='module' and b['labels']==[name])
            self.assertNotIn('count',call['attrs'])
        log=next(b for b in root if b['kind']=='resource' and b['labels']==['aws_cloudwatch_log_group','backend'])
        self.assertNotIn('count', log['attrs'])
        self.assertIn('prevent_destroy = true',log['body'])
        db=(BASE/'modules/mysql/main.tf').read_text()
        for setting in ['prevent_destroy = true','deletion_protection = true','skip_final_snapshot = false','backup_retention_period = 7','value = "ON"']:
            self.assertIn(setting,db)

    def test_bootstrap_and_hcp_task_ownership_contract(self):
        self.assertEqual(self.variables['backend_desired_count']['attrs']['default'],'0')
        self.assertEqual(self.variables['backend_max_instances']['attrs']['default'],'1')
        backend=(BASE/'modules/ecs-backend/main.tf').read_text()
        for setting in ['instance_type        = "t3.small"','ECS_RESERVED_MEMORY=512','memory = 1024','hostPort = 8080','wait_for_steady_state = true','task_definition = aws_ecs_task_definition.initial.arn','aws_autoscaling_group.host]']:
            self.assertIn(setting,backend)
        self.assertNotIn('ignore_changes = [task_definition]',backend)
        self.assertNotIn('task_role_arn',backend)
        self.assertIn('ignore_changes = [desired_capacity]',backend)
        self.assertIn('managed_draining = "ENABLED"',backend)

    def test_strict_origin_and_private_network_contracts(self):
        alb=(BASE/'modules/alb/main.tf').read_text()
        network=(BASE/'modules/networking/main.tf').read_text()
        for setting in ['matcher = "200"','target_type = "instance"','status_code  = "403"','values = [var.origin_header]']:
            self.assertIn(setting,alb)
        self.assertIn('com.amazonaws.global.cloudfront.origin-facing',network)
        self.assertIn('referenced_security_group_id = aws_security_group.alb.id',network)
        self.assertIn('referenced_security_group_id = aws_security_group.backend.id',network)
        self.assertNotIn('from_port = 22',network)
        self.assertNotIn('aws_nat_gateway',network)
        self.assertIn('cidrsubnet(var.vpc_cidr, 8, 10 + count.index)',network)

    def test_release_draft_cannot_compete_with_hcp(self):
        draft=(ROOT/'infrastructure/ci/application-release.yml.example').read_text()
        self.assertIn('if: ${{ false }}',draft)
        self.assertNotIn('aws ecs update-service',draft)
        self.assertNotIn('aws ecs register-task-definition',draft)
        self.assertNotIn('terraform apply',draft)
        self.assertIn('RELEASE_IMAGE',draft)
