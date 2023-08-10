import os
import json
import re
import logging
import hmac
import hashlib
import boto3


branch_prefix = os.getenv("branch_prefix")
cfn_pipeline_suffix = os.getenv("cfn_pipeline_suffix")
pipeline_template = os.getenv("pipeline_template")

codepipeline_client = boto3.client("codepipeline")
sm_client = boto3.client("secretsmanager")
ssm_client = boto3.client("ssm")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_github_webhook_secret_from_secretsmanager(github_webhook_secret):
    response = sm_client.get_secret_value(
        SecretId=github_webhook_secret,
    )
    if "SecretString" in response:
        secret = json.loads(response["SecretString"]).get(github_webhook_secret)
    return secret


def branch_name_check(branch_name, branch_prefix):
    #return True
    # implement if needed
    if re.match(branch_prefix, branch_name):
        return True
    else:
        return False


def verify_webhook(secret, data, hmac_header):
    received_hmac = re.sub(r"^sha256=", "", hmac_header)
    hexdigest = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return hexdigest == received_hmac





def save_branch_name_in_ssm(branch_name):
    branch_chars = re.sub("[^0-9a-zA-Z-]+", "", str(branch_name))

    response = ssm_client.put_parameter(
        Name=branch_chars, Value=branch_name, Type="String", Overwrite=True
    )


def delete_branch_name_in_ssm(branch_name):
    branch_chars = re.sub("[^0-9a-zA-Z-]+", "", str(branch_name))

    response = ssm_client.delete_parameter(Name=branch_chars)


def create_feature_pipeline_from_template(
    branch_name, pipeline_template, pipeline_name
):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.get_pipeline(
        name=pipeline_template,
    )

    pipeline_describe = response.get("pipeline", {})

    pipeline_describe["name"] = pipeline_name
    pipeline_describe["stages"][0]["actions"][0]["configuration"][
        "BranchName"
    ] = branch_name

    response = codepipeline_client.create_pipeline(pipeline=pipeline_describe)


def delete_feature_pipeline(pipeline_name):
    codepipeline_client = boto3.client("codepipeline")
    response = codepipeline_client.delete_pipeline(name=pipeline_name)


def handler(event, context):
    #raw_body_data = event.get("body", {})
    raw_body_data = json.loads(event.get("body", {}))
    print(raw_body_data)
    #logger.info(raw_body_data)
    body = raw_body_data.get("data")
    event = raw_body_data.get("event")
    print("event")
    print(body)  
    msg = "" 
    try:
            secret = get_github_webhook_secret_from_secretsmanager("github_webhook_secret")
            ref = body.get("ref", "")
            ref_head = body.get("ref_head", "")
            ref_type = body.get("ref_type", "")
            #description = dict_haskey(body, "description") # commit message
            description = body.get("description", "")
            logger.info(f"ref: {ref}, ref_type: {ref_type}, description: {description}")

            if ref_type == "branch":
                branch_name = ref
                # create pipeline 
                if description:
                    if branch_name_check(branch_name, branch_prefix):
                        logger.info(f"Saving branch name to parameter store: {branch_name}")
                        save_branch_name_in_ssm(branch_name)

                        branch_chars = re.sub("[^0-9a-zA-Z-]+", "", str(branch_name))
                        pipeline_name = branch_chars + cfn_pipeline_suffix
                        logger.info(
                            f"Generating pipeline {pipeline_name} for branch: {branch_name}"
                        )
                        create_feature_pipeline_from_template(
                            branch_name, pipeline_template, pipeline_name
                        )

                        msg = f"Done feature pipeline generation for: {branch_name}"
                    else:
                        msg = f"Branch name {branch_name} does not match the prefix {branch_prefix}"

                else:
                    ## delete pipeline on PR close
                    branch_name = ref_head
                    if branch_name_check(branch_name, branch_prefix):
                        logger.info(f"Deleting branch name from parameter store: {branch_name}")
                        delete_branch_name_in_ssm(branch_name)

                        branch_chars = re.sub("[^0-9a-zA-Z-]+", "", str(branch_name))
                        pipeline_name = branch_chars + cfn_pipeline_suffix
                        logger.info(
                            f"Dropping pipeline {pipeline_name} for branch: {branch_name}"
                        )
                        delete_feature_pipeline(pipeline_name)

                        msg = f"Done feature pipeline deletion for: {branch_name}"
                    else:
                        msg = f"Branch name {branch_name} does not match the prefix {branch_prefix}"

            else:
                msg = 'Not one of the following events: ["Branch creation", "Branch deletion"]'

    except Exception as e:
        msg = f"Error: {str(e)}"

    logger.info(msg)
    return {"statusCode": 200, "body": json.dumps(msg)}