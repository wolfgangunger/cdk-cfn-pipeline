#!/usr/bin/env python3
import os

from aws_cdk import (
    App,
)

from infrastructure.cicd.pipeline_generator_stack import PipelineGeneratorStack
from generic.infrastructure.iam.bootstrap_role_stack import BootstrapRoleStack

app = App()

# Read the config from cdk.json
config = app.node.try_get_context("config")
accounts = config.get("accounts")
region: str = accounts["tooling"]["region"]
dev_account: str = accounts["dev"]["account"]
qa_account: str = accounts["qa"]["account"]
prod_account: str = accounts["prod"]["account"]


### Bootstrap Role Stacks only to run in the first time. Comment out after creation
# iam role for pipeline deploy dev enviroment stacks
BootstrapRoleStack(
    app,
    "bootstrap-dev-role-stack",
    account="dev",
    toolchain_account=accounts.get("tooling").get("account"),
    env={
        "account": dev_account,
        "region": region,
    },
)
# iam role for pipeline deploy qa enviroment stacks
BootstrapRoleStack(
    app,
    "bootstrap-qa-role-stack",
    account="dev",
    toolchain_account=accounts.get("tooling").get("account"),
    env={
        "account": qa_account,
        "region": region,
    },
)
# iam role for pipeline deploy prod enviroment stacks
BootstrapRoleStack(
    app,
    "bootstrap-prod-role-stack",
    account="dev",
    toolchain_account=accounts.get("tooling").get("account"),
    env={
        "account": prod_account,
        "region": region,
    },
)



config = app.node.try_get_context("config")
accounts = config.get("accounts")

branch_name = "main"
#pipeline_template = "feature-branch-pipeline-template"
pipeline_template = "cfn-deploy-pipeline-template"
PipelineGeneratorStack(
    app,
    "cfn-deploy--pipeline-generator",
    branch_name=branch_name,
    pipeline_template=pipeline_template,
    branch_prefix="^(feature|bug|hotfix)/",
    cfn_pipeline_suffix="-CFN-Pipeline",
    env=accounts.get("tooling"),
    config={**config},
)

app.synth()
