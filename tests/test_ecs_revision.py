"""Offline release fixtures only: no AWS calls or real credentials."""
import copy
import unittest
from scripts.prepare_ecs_revision import prepare


class RevisionTest(unittest.TestCase):
    def setUp(self):
        self.account="123456789012"
        self.task="arn:aws:iam::123456789012:role/climatehealth-task"
        self.execution="arn:aws:iam::123456789012:role/climatehealth-execution"
        self.image="123456789012.dkr.ecr.us-east-1.amazonaws.com/climatehealth@sha256:"+"a"*64
        self.base={"family":"climatehealth", "networkMode":"bridge", "taskRoleArn":self.task,
                   "executionRoleArn":self.execution,"revision":3,"status":"ACTIVE",
                   "containerDefinitions":[{"name":"backend","image":"old","memory":1024,
                        "secrets":[{"name":"DB_PASS","valueFrom":"test-parameter-reference"}]}]}

    def call(self,base=None,image=None):
        return prepare(base or self.base,image or self.image,"climatehealth",self.account,self.task,self.execution)

    def test_immutable_revision_preserves_reviewed_config_not_response_metadata(self):
        before=copy.deepcopy(self.base);result=self.call()
        self.assertEqual(result["containerDefinitions"][0]["image"],self.image)
        self.assertEqual(result["containerDefinitions"][0]["memory"],1024)
        self.assertEqual(result["containerDefinitions"][0]["secrets"],self.base["containerDefinitions"][0]["secrets"])
        self.assertNotIn("revision",result);self.assertNotIn("status",result)
        self.assertEqual(self.base,before)

    def test_wrong_image_account_role_network_and_plaintext_rejected(self):
        for image in ["repo:latest",self.image.replace(self.account,"999999999999")]:
            with self.assertRaises(ValueError):self.call(image=image)
        for key,value in [("family","other"),("networkMode","awsvpc"),("taskRoleArn","wrong")]:
            base=copy.deepcopy(self.base);base[key]=value
            with self.assertRaises(ValueError):self.call(base)
        base=copy.deepcopy(self.base);base["containerDefinitions"][0]["environment"]=[{"name":"DB_PASS","value":"synthetic-only"}]
        with self.assertRaises(ValueError):self.call(base)
