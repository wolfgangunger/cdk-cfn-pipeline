from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    pipelines,
    aws_codebuild,
    CfnCapabilities
)

import aws_cdk.aws_codepipeline_actions as cpactions
import aws_cdk.aws_codepipeline as codepipeline
        

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
        repo_owner = config.get("owner")
        repo_cfn = config.get("repo_cfn")
        connection_arn = config.get("connection_arn")
        source_output = codepipeline.Artifact("SourceArtifact")
        stack_name = "template-005" 
        ## todo 
        template = ""
        stage = ""


        source_action = cpactions.CodeStarConnectionsSourceAction(
            action_name="Github_Source",
            owner=repo_owner,
            repo=repo_cfn,
            branch="main",
            output=source_output,
            connection_arn=connection_arn
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




    



