from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    pipelines,
    aws_codebuild,
    Duration,
)
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodePipeline

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
        super().__init__(scope, id, **kwargs)

        accounts = config.get("accounts")
        region: str = accounts["tooling"]["region"]
        dev_account: str = accounts["dev"]["account"]
        qa_account: str = accounts["qa"]["account"]
        toolchain_account: str = accounts["tooling"]["account"]
        prod_account: str = accounts["prod"]["account"]
        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")

        synth_dev_account_role_arn = (
            f"arn:aws:iam::{dev_account}:role/codebuild-role-from-toolchain-account"
        )

        synth_qa_account_role_arn = (
            f"arn:aws:iam::{qa_account}:role/codebuild-role-from-toolchain-account"
        )
        synth_prod_account_role_arn = (
            f"arn:aws:iam::{prod_account}:role/codebuild-role-from-toolchain-account"
        )

        # creating the pipline with  synch action
        git_input = self.get_connection(repo_owner,repo,config,development_pipeline,codestar_connection_arn)
        
        synth_step = self.get_synth_step(
            git_input,
            synth_dev_account_role_arn,
            synth_qa_account_role_arn,
            synth_prod_account_role_arn,
        )

        pipeline = CodePipeline(
            self,
            id,
            #
            pipeline_name=id,   
            #            
            synth=synth_step,
            cross_account_keys=True,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                )
            ),
        )





        if development_pipeline:
  

            # Dev deploy
            dev_app = AppDeploy(
                self,
                "dev",
                config=config,
                env={
                    "account": dev_account,
                    "region": region,
                },
            )
            ## deploy dev stack
            dev_stage = pipeline.add_stage(dev_app)


            ## QA deploy
            qa_app = AppDeploy(
                self,
                "qa",
                config=config,
                env={
                    "account": qa_account,
                    "region": region,
                },
            )
            qa_stage = pipeline.add_stage(qa_app)

        else:


            # Deploy Prod
            prod_app = AppDeploy(
                self,
                "prod",
                config=config,
                env={
                    "account": prod_account,
                    "region": region,
                },
            )
            prod_stage = pipeline.add_stage(prod_app)

   
    def get_connection(
        self,
        repo_owner,
        repo,
        config,
        development_pipeline,
        codestar_connection_arn
    ):
        git_input = pipelines.CodePipelineSource.connection(
            repo_string=f"{repo_owner}/{repo}",
            branch=config["development_branch"]
            if development_pipeline
            else config["production_branch"],
            connection_arn=codestar_connection_arn,
        )
        return git_input
    
    def get_synth_step(
        self,
        git_input,
        synth_dev_account_role_arn,
        synth_qa_account_role_arn,
        synth_prod_account_role_arn,
    ):
        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=git_input,
            commands=self.get_synth_step_commands(),
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        synth_dev_account_role_arn,
                        synth_qa_account_role_arn,
                        synth_prod_account_role_arn,
                    ],
                ),
            ],
        )
        return synth_step

    def get_synth_step_commands(self) -> list:
        commands = [
            "npm install -g aws-cdk",
            "python -m pip install -r requirements.txt",
            "cdk list && cdk synth",
        ]
        return commands


