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
# directory/folder path
dir_path = r'.'
# dict to store files
#res = []
templates = {}

def is_folder_name_in_ssm(folder_name):
    #folder_chars = re.sub("[^0-9a-zA-Z-]+", "", str(folder_name))
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
    #folder_chars = re.sub("[^0-9a-zA-Z-]+", "", str(folder_name))

    response = ssm_client.put_parameter(
        Name=folder_name, Value=folder_name, Type="String", Overwrite=True
    )

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
        else:
            print ("ssm param already exists: " + key)  
