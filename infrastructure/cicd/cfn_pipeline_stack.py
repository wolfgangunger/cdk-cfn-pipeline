from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    pipelines,
    aws_codebuild,
    CfnCapabilities
)
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodePipeline
import aws_cdk.aws_codepipeline_actions as cpactions
import aws_cdk.aws_codepipeline as codepipeline
from infrastructure.cicd.app_deploy import AppDeploy
        

class CfnPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        development_pipeline: bool,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, stack_name=id, **kwargs)

        accounts = config.get("accounts")
        region: str = accounts["tooling"]["region"]
        dev_account: str = accounts["dev"]["account"]
        qa_account: str = accounts["qa"]["account"]
        toolchain_account: str = accounts["tooling"]["account"]
        prod_account: str = accounts["prod"]["account"]
        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo_cfn")
     

        source_output = codepipeline.Artifact("SourceArtifact")
        stack_name = "template-005"


        source_action = cpactions.CodeStarConnectionsSourceAction(
            action_name="Github_Source",
            owner="wolfgangunger",
            repo="sam-cfn-pipeline-test",
            branch="main",
            output=source_output,
            connection_arn="arn:aws:codestar-connections:eu-west-1:039735417706:connection/8c2fcdc0-36a2-4942-b8eb-d9c9837e4fe2"
        )

        pipeline = codepipeline.Pipeline(self, "CFN-Pipeline", pipeline_name = id,
        stages=[
            codepipeline.StageProps(
            stage_name="Source",
            actions=[
                    source_action
                 ]
              )     ,       
            codepipeline.StageProps(
            stage_name="CFN-Deploy",
            actions=[
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
              )
            ]
         )




    



