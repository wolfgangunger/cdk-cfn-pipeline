from constructs import Construct
from aws_cdk import Stack, aws_iam as iam, pipelines, aws_codebuild, CfnCapabilities

import aws_cdk.aws_codepipeline_actions as cpactions
import aws_cdk.aws_codepipeline as codepipeline
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk import PhysicalName

class CfnPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        account_role_arn,
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
            connection_arn=connection_arn,
        )

        action_role = iam.Role(self, "ActionRole",
            assumed_by=iam.AccountPrincipal("039735417706"),
            # the role has to have a physical name set
            role_name=PhysicalName.GENERATE_IF_NEEDED,
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCloudFormationFullAccess"
                )
            #     iam.ManagedPolicy.from_aws_managed_policy_name(
            #         'AdministratorAccess')
            ]
        )
        ##
        pipeline = codepipeline.Pipeline(
            self,
            "CFN-Pipeline",
            pipeline_name=id,
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(
                    stage_name="CFN-Deploy",
                    actions=[
                        cpactions.CloudFormationCreateUpdateStackAction(
                            action_name="Deploy_CFN_Template",
                            stack_name=stack_name,
                            admin_permissions=True,
                            template_path=source_output.at_path(
                                "cfn_00x_to_be_replaced/template.yaml"
                            ),
                            template_configuration=source_output.at_path(
                                "cfn_00x_to_be_replaced/params_dev.json"
                            ),
                            run_order=1,
                            role=action_role
                        )
                    ],
                ),
            ],
        )
