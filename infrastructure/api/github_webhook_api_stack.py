import os
import json

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam,
    aws_lambda,
    aws_apigateway,
    aws_logs,
    Duration,
    CfnOutput,
    aws_secretsmanager
)

from aws_cdk.aws_lambda_python_alpha import PythonFunction


class GithubWebhookAPIStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        pipeline_template: str,
        branch_prefix: str,
        cfn_pipeline_suffix: str,
        config: dict,
        **kwargs,
    ) -> None:
        """
        Creates the following infrastructure:
            API Gateway
            Lambda
            IAM Role
        """
        super().__init__(scope, id, **kwargs)

        # create secret     
        secret = aws_secretsmanager.Secret(
            self, 
            "github_webhook_secret",
            secret_name = "github_webhook_secret"
        )

        # Create an IAM Role for use with lambda
        handler_role = aws_iam.Role(
            self,
            id="generator-lambda-role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{id}-lambda-role",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        handler_role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "ssm:PutParameter",
                    "ssm:DeleteParameter",
                    "ssm:GetParameter",
                    "iam:PassRole",
                    "secretsmanager:GetSecretValue",
                    "codepipeline:CreatePipeline",
                    "codepipeline:DeletePipeline",
                    "codepipeline:ListPipelines",
                    "codepipeline:GetPipeline",
                    "codepipeline:UpdatePipeline",
                    "codestar-connections:PassConnection",
                ],
                resources=["*"],
            )
        )

        # Create a lambda function that can act as a handler for API Gateway requests
        integration_handler_lambda_function = PythonFunction(
            self,
            id="githubWebhookApiHandler",
            # function_name=f"{id}-handler",
            function_name=f"github-handler",
            entry=os.path.join(
                os.getcwd(), "infrastructure", "lambdas", "github_webhook_api"
            ),
            index="github_webhook.py",
            role=handler_role,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            environment={
                "pipeline_template": pipeline_template,
                "branch_prefix": branch_prefix,
                "cfn_pipeline_suffix": cfn_pipeline_suffix,
            },
            memory_size=1024,
            timeout=Duration.minutes(1),
        )
        CfnOutput(
            self,
            f"{id}-github-webhook-api-handler-lambda-arn",
            value=integration_handler_lambda_function.function_arn,
            export_name=f"{id}-github-webhook-api-handler-lambda-arn",
        )

        # Create a REST API using API Gateway
        log_group = aws_logs.LogGroup(self, "Github-Webhook-API-Logs")
        deploy_options = aws_apigateway.StageOptions(
            access_log_destination=aws_apigateway.LogGroupLogDestination(log_group),
            access_log_format=aws_apigateway.AccessLogFormat.json_with_standard_fields(
                caller=False,
                http_method=True,
                ip=True,
                protocol=True,
                request_time=True,
                resource_path=True,
                response_length=True,
                status=True,
                user=True,
            ),
            metrics_enabled=True,
        )
        github_webhook_api_gateway = aws_apigateway.RestApi(
            self,
            f"{id}-api-gateway",
            deploy_options=deploy_options,
            default_cors_preflight_options={
                "allow_origins": aws_apigateway.Cors.ALL_ORIGINS,
                "allow_methods": aws_apigateway.Cors.ALL_METHODS,
            },
        )
        CfnOutput(
            self,
            f"{id}-api-gateway-domain-arn",
            value=github_webhook_api_gateway.arn_for_execute_api(),
            export_name=f"{id}-api-gateway-domain-arn",
        )

        # Connect the handler lambda function to API Gateway
        lambda_integration = aws_apigateway.LambdaIntegration(
            integration_handler_lambda_function,
            proxy=True,
        )

        # Add endpoint
        webhooks_resource = github_webhook_api_gateway.root.add_resource("webhook")

        webhooks_resource.add_method(
            "POST",
            lambda_integration,
        )
