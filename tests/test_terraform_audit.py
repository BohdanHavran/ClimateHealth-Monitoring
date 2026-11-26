"""Offline audit-tool regressions using synthetic HCL, without AWS or Terraform."""
import tempfile
import unittest
from pathlib import Path
from scripts.audit_terraform import blocks, traversals, build, serializable, read_inventory
import json


class TerraformAuditTests(unittest.TestCase):
    def test_json_roundtrip_preserves_attribute_names_and_expressions(self):
        graph={'nodes':[{'attrs':{'setting':'var.input','count':'var.mode == "rds" ? 1 : 0'}}], 'blocks':[]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'inventory.json'
            p.write_text(json.dumps(serializable(graph)))
            self.assertEqual(read_inventory(p),graph)

    def test_comparison_is_not_an_attribute_assignment(self):
        source = 'resource "aws_instance" "example" {\n count = var.mode == "rds" ? 1 : 0\n ami = var.ami\n}\n'
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'main.tf';p.write_text(source)
            b = blocks(p,Path(tmp))[0]
        self.assertEqual(b['attrs']['count'], 'var.mode == "rds" ? 1 : 0')
        self.assertEqual(b['attrs']['ami'], 'var.ami')

    def test_templates_comments_and_datasource_prefix(self):
        refs=traversals('data.aws_region.current.region + "literal var.fake ${var.real}" # var.hidden\n')
        self.assertIn(['data','aws_region','current','region'], refs)
        self.assertIn(['var','real'], refs)
        self.assertNotIn(['var','fake'], refs)
        self.assertNotIn(['var','hidden'], refs)
        self.assertNotIn(['aws_region','current','region'], refs)

    def test_indexed_module_output_and_index_variable(self):
        refs=traversals('module.alb[0].dns + aws_instance.node[var.slot].id')
        self.assertIn(['module','alb','dns'], refs)
        self.assertIn(['var','slot'], refs)

    def test_heredoc_only_hcl_interpolation_is_a_reference(self):
        refs=traversals('<<-JS\nvar request = event.request; // var.fake\n${aws_ecs_cluster.this.name}\nJS\n')
        self.assertEqual(refs,[['aws_ecs_cluster','this','name']])

    def test_input_output_bindings_do_not_invent_resource_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); child=base/'modules/sample';child.mkdir(parents=True)
            (base/'main.tf').write_text('variable "x" { type = string }\nprovider "aws" { region = "region-is-not-executed" }\nmodule "sample" {\n source = "./modules/sample"\n name = var.x\n}\noutput "result" { value = module.sample.result }\n')
            (child/'main.tf').write_text('variable "name" { type = string }\nresource "aws_s3_bucket" "example" { bucket = var.name }\noutput "result" { value = aws_s3_bucket.example.id }\n')
            g=build(base)
        self.assertFalse(g['unresolved'])
        pairs={(e['source'],e['target'],e['relation']) for e in g['edges']}
        self.assertIn(('root::module.sample.input.name','module.sample::var.name','input_binding'),pairs)
        self.assertIn(('module.sample::output.result','root::output.result','reference'),pairs)
        self.assertIn(('root::provider.aws','module.sample::aws_s3_bucket.example','provider'),pairs)


if __name__ == '__main__':
    unittest.main()
