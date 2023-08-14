#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create the cfn pipelines and store cfn template in ssm
"""

import os
import boto3
import json
import re

ssm_client = boto3.client("ssm")
codepipeline_client = boto3.client("codepipeline")
sm_client = boto3.client("secretsmanager")

branch_chars = ""
branch_name = ""
stage = "dev"
folder_prefix = "cfn_"
pipeline_template = "cfn-pipeline-template"
pipeline_name = "cfn-pipeline-"

dir_path = r'.'
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

def delete_folder_name_in_ssm(folder_name):
    response = ssm_client.delete_parameter(
      Name=folder_name
     )  
###
def create_cfn_pipeline_from_template( stage, pipeline_template, key):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.get_pipeline(
        name=pipeline_template,
    )

    pipeline_describe = response.get("pipeline", {})

    pipeline_describe["name"] = key

    pipeline_describe["stages"][0]["actions"][0]["configuration"][
        "BranchName"
    ] = "main"

    pipeline_describe["stages"][1]["actions"][0]["configuration"][
        "StackName"
    ] = key.replace("_","-")
    
    pipeline_describe["stages"][1]["actions"][0]["configuration"][
        "TemplateConfiguration"
    ] =  "SourceArtifact::" + key + "/params_" + stage + ".json"
     
    pipeline_describe["stages"][1]["actions"][0]["configuration"][
        "TemplatePath"
    ] =  "SourceArtifact::" + key + "/template.yaml"   

    response = codepipeline_client.create_pipeline(pipeline=pipeline_describe)

def delete_cfn_pipeline(key):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.delete_pipeline(name=key)

##########################
if __name__ == "__main__":

    print("create pipelines for cfn templates")
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        if not os.path.isfile(os.path.join(dir_path, file_path)):
            if file_path.startswith(folder_prefix):
              vars = open(file_path + "/params_" + stage + ".json")
              data = json.load(vars)
              templates[file_path] = data


    # print(templates)
    # print("###")
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
            #stage, pipeline_template, pipeline_name + key
            stage, pipeline_template,   key    
          )
          msg = f"Done feature pipeline generation for: {branch_name}"
        else:
            print ("ssm param already exists: " + key)  

     ### delete pipeline and parameter
    print("delete pipelines")
    p = ssm_client.get_paginator('describe_parameters')
    paginator = p.paginate().build_full_result()
    for page in paginator['Parameters']:
        response = ssm_client.get_parameter(Name=page['Name'])
        p_name = response.get("Parameter").get("Name")
        print(p_name)
        if p_name.startswith("cfn"):
            print("cfn parameter")
            if not p_name in templates:
                print ("deleting pipeline for " + p_name)
                delete_cfn_pipeline( p_name)
                #delete parameter
                print("delete parameter for " + p_name)
                delete_folder_name_in_ssm(p_name)
        else:
            print("no cfn parameter")     
 
