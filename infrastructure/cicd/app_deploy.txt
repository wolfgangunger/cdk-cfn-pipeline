from aws_cdk import Stage, DefaultStackSynthesizer
from constructs import Construct
import aws_cdk.aws_codepipeline_actions as cpactions
from infrastructure.data.s3bucket_stack import S3Stack


class AppDeploy(Stage):
    def __init__(self, scope: Construct, id: str, source_output: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        # s3 bucket Stack Example
        #s3bucket = S3Stack(self, "S3Stack")
        stack_name = "template-005"
        #change_set_name = "StagedChangeSet"
        #cfn_capabilities = CfnCapabilities(CfnCapabilities.NAMED_IAM)
        cfn_deploy = {
            "stage_name": "Deploy",
            "actions": [
                cpactions.CloudFormationCreateUpdateStackAction(
                    action_name="Deploy_CFN_Template",
                    stack_name=stack_name,
                    #change_set_name=change_set_name,
                    admin_permissions=True,
                    template_path=source_output.at_path("aws-005-test-roles/template.yaml"),
                    template_configuration=source_output.at_path("aws-005-test-roles/vars_dev.json"),
                    run_order=1
                    #cfn_capabilities=["CAPABILITY_IAM","CAPABILITY_NAMED_IAM"]
                    #cfn_capabilities=[CfnCapabilities.NAMED_IAM]
                    #cfn_capabilities=cfn_capabilities
                    
                )
            ]
        }
        


