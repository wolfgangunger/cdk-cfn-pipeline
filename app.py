#!/usr/bin/env python3
import os

from aws_cdk import (
    App,
)

from infrastructure.cicd.pipeline_generator_stack import PipelineGeneratorStack
from infrastructure.iam.bootstrap_role_stack import BootstrapRoleStack

app = App()

# Read the config from cdk.json
config = app.node.try_get_context("config")
accounts = config.get("accounts")
region: str = accounts["tooling"]["region"]
account: str = accounts["tooling"]["account"]


# iam role for pipeline deploy 
BootstrapRoleStack(
    app,
    "bootstrap-role-stack",
    account="dev",
    toolchain_account=account,
    env={
        "account": account,
        "region": region,
    },
)

branch_name = config.get("branch")
branch_name_cfn = config.get("branch_cfn")

PipelineGeneratorStack(
    app,
    "cfn-deploy--pipeline-generator",
    branch_name=branch_name,
    branch_name_cfn=branch_name_cfn,
    env=accounts.get("tooling"),
    config={**config},
)

app.synth()
