#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get branch name from Parameter Store
In the feature branch pipeline, the script is used for getting feature branch name from ssm
"""

import os
import boto3

ssm_client = boto3.client("ssm")

feature_pipeline_suffix = os.getenv("feature_pipeline_suffix")
branch_chars = ""
branch_name = ""

if __name__ == "__main__":
    # CODEBUILD_INITIATOR="codepipeline/feature-branch-pipeline"
    CODEBUILD_INITIATOR_LIST = os.getenv("CODEBUILD_INITIATOR").split("/")
    if len(CODEBUILD_INITIATOR_LIST) >= 2:
        if CODEBUILD_INITIATOR_LIST[0] == "codepipeline":
            branch_chars = CODEBUILD_INITIATOR_LIST[-1].replace(
                feature_pipeline_suffix, ""
            )
            if branch_chars:
                response = ssm_client.get_parameter(
                    Name=branch_chars,
                )
                branch_name = response.get("Parameter", {}).get("Value", "")
                print(branch_name)
