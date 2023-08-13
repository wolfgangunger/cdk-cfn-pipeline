from aws_cdk import (
    DefaultStackSynthesizer,
    Stack,
    Stage,
)

from constructs import Construct
import aws_cdk.aws_iam as aws_iam
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import pipelines
from aws_cdk import aws_codebuild
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodePipeline

from infrastructure.cicd.cfn_pipeline_stack import CfnPipelineStack


# the stage to deploy the cfn-pipeline template
class PipelineGeneratorApplicationBootstrap(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        pipeline_template: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # a template pipeline for each cloudformation stack
        CfnPipelineStack(
            self,
            "cfn-pipeline-template",
            config={**config},
            synthesizer=DefaultStackSynthesizer(),
        )


# the pipeline generator itself
class PipelineGeneratorStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        branch_name: str,
        branch_name_cfn: str,
        pipeline_template: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        accounts = config.get("accounts")
        dev_account: str = accounts["dev"]["account"]
        qa_account: str = accounts["qa"]["account"]
        toolchain_account: str = accounts["tooling"]["account"]
        prod_account: str = accounts["prod"]["account"]
        region: str = accounts["tooling"]["region"]

        synth_dev_account_role_arn = (
            f"arn:aws:iam::{dev_account}:role/codebuild-role-from-toolchain-account"
        )

        synth_qa_account_role_arn = (
            f"arn:aws:iam::{qa_account}:role/codebuild-role-from-toolchain-account"
        )
        synth_prod_account_role_arn = (
            f"arn:aws:iam::{prod_account}:role/codebuild-role-from-toolchain-account"
        )

        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")
        repo_cfn = config.get("repo_cfn")
        # repo_cfn = "sam-cfn-pipeline-test"

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # git input for the generator pipeline itself, the cdk repo
        git_input = pipelines.CodePipelineSource.connection(
            repo_string=f"{repo_owner}/{repo}",
            branch=branch_name,
            connection_arn=codestar_connection_arn,
        )
        # git input for the cfn repo
        git_input_cfn = pipelines.CodePipelineSource.connection(
            repo_string=f"{repo_owner}/{repo_cfn}",
            branch=branch_name_cfn,
            connection_arn=codestar_connection_arn,
        )

        # creating the generator pipline with  synch action
        synth_step = self.get_sync_step(
            git_input,
            synth_dev_account_role_arn,
            synth_qa_account_role_arn,
            synth_prod_account_role_arn,
            branch_name,
        )

        pipeline = CodePipeline(
            self,
            id,
            pipeline_name=id,
            synth=synth_step,
            cross_account_keys=True,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                )
            ),
        )

        pipeline_generator_bootstrap_stage = PipelineGeneratorApplicationBootstrap(
            self,
            "pipeline-generator-bootstrap-stage",
            pipeline_template=pipeline_template,
            config=config,
            env={
                "account": toolchain_account,
                "region": region,
            },
        )
        dev_bootstrap_stage = pipeline.add_stage(pipeline_generator_bootstrap_stage)

        # action for creating the pipelines
        create_cfn_pipelines_step = self.create_cfn_pipelines_step(
            git_input_cfn,
            git_input,
            synth_step,
            synth_dev_account_role_arn,
            branch_name,
        )
        wave = pipeline.add_wave(
            "Create_Cfn_Pipelines", post=[create_cfn_pipelines_step]
        )

    ###

    def get_sync_step(
        self,
        git_input,
        synth_dev_account_role_arn,
        synth_qa_account_role_arn,
        synth_prod_account_role_arn,
        branch_name,
    ):
        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=git_input,
            commands=self.get_sync_step_commands(),
            env={"BRANCH": branch_name},
            role_policy_statements=[
                aws_iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=[
                        synth_dev_account_role_arn,
                        synth_qa_account_role_arn,
                        synth_prod_account_role_arn,
                    ],
                ),
            ],
        )
        return synth_step

    ###
    def get_sync_step_commands(self) -> list:
        commands = [
            "npm install -g aws-cdk",
            "python -m pip install -r requirements.txt",
            "echo branch: $BRANCH; cdk list -c branch_name=$BRANCH",
            "echo branch: $BRANCH; cdk synth -c branch_name=$BRANCH",
        ]
        return commands

    def create_cfn_pipelines_step(
        self,
        git_input_cfn,
        git_input,
        synth_step,
        synth_dev_account_role_arn,
        branch_name,
    ):
        cfn_repo_step = pipelines.CodeBuildStep(
            "Create CFN Pipelines",
            input=git_input_cfn,
            additional_inputs={"subdir": git_input, "./cdk_input": synth_step},
            commands=self.create_cfn_pipelines_step_commands(),
            env={"BRANCH": branch_name},
            role_policy_statements=[
                aws_iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=[
                        synth_dev_account_role_arn,
                    ],
                ),
                aws_iam.PolicyStatement(
                    actions=["ssm:*"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
                aws_iam.PolicyStatement(
                    actions=["cloudformation:*"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
                aws_iam.PolicyStatement(
                    actions=["codepipeline:*"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),            
            ],
        )
        return cfn_repo_step

    def create_cfn_pipelines_step_commands(self) -> list:
        commands = [
            "pwd",
            "ls",
            "python subdir/infrastructure/scripts/create_pipelines.py",
        ]
        return commands
