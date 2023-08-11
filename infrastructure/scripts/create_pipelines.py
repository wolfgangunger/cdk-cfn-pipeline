#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get branch name from Parameter Store
In the feature branch pipeline, the script is used for getting feature branch name from ssm
"""

import os
import boto3

ssm_client = boto3.client("ssm")
codepipeline_client = boto3.client("codepipeline")
sm_client = boto3.client("secretsmanager")

feature_pipeline_suffix = os.getenv("feature_pipeline_suffix")
branch_chars = ""
branch_name = ""
# directory/folder path
dir_path = r'.'
# list to store files
res = []
dirs = []

if __name__ == "__main__":

    print("create pipelines for cfn templates")
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        if not os.path.isfile(os.path.join(dir_path, file_path)):
            if file_path.startswith("aws"):
            # add filename to list
             dirs.append(file_path)


    print(dirs)
