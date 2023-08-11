#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get branch name from Parameter Store
In the feature branch pipeline, the script is used for getting feature branch name from ssm
"""

import os
import boto3
import json
import re

ssm_client = boto3.client("ssm")
codepipeline_client = boto3.client("codepipeline")
sm_client = boto3.client("secretsmanager")

feature_pipeline_suffix = os.getenv("feature_pipeline_suffix")
branch_chars = ""
branch_name = ""
stage = "dev"
folder_prefix = "cfn_"
pipeline_template = "cfn-pipeline-template"
pipeline_name = "cfn-pipeline-"

# directory/folder path
dir_path = r'.'
# dict to store files
#res = []
templates = {}

def is_folder_name_in_ssm(folder_name):
    try:
        response = ssm_client.get_parameter(
        Name=folder_name,
        WithDecryption=True|False
        ) 
        print ("exists")
        return response
    except ssm_client.exceptions.ParameterNotFound:
         print("not exists")  
         return None 

   
def save_folder_name_in_ssm(folder_name):
    response = ssm_client.put_parameter(
        Name=folder_name, Value=folder_name, Type="String", Overwrite=True
    )

def create_cfn_pipeline_from_template( stage, pipeline_template, pipeline_name):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.get_pipeline(
        name=pipeline_template,
    )

    pipeline_describe = response.get("pipeline", {})

    pipeline_describe["name"] = pipeline_name
    # pipeline_describe["stages"][0]["actions"][0]["configuration"][
    #     "Stage"
    # ] = stage
    pipeline_describe["stages"][0]["actions"][0]["configuration"][
        "BranchName"
    ] = "main"

    response = codepipeline_client.create_pipeline(pipeline=pipeline_describe)

def delete_cfn_pipeline(pipeline_name):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.delete_pipeline(name=pipeline_name)

if __name__ == "__main__":

    print("create pipelines for cfn templates")
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        if not os.path.isfile(os.path.join(dir_path, file_path)):
            if file_path.startswith(folder_prefix):
              vars = open(file_path + "/vars_" + stage + ".json")
              data = json.load(vars)
              templates[file_path] = data


    print(templates)
    print("###")
    for key in templates:
        print(key)
        # check ssm
        exists = is_folder_name_in_ssm(key)
        if not exists:
          print("create ssm for " + key)
          save_folder_name_in_ssm(key)
          #create pipeline
          print("create pipeline for " + key)
          create_cfn_pipeline_from_template(
            stage, pipeline_template, pipeline_name + key
          )
          msg = f"Done feature pipeline generation for: {branch_name}"
        else:
            print ("ssm param already exists: " + key)  
