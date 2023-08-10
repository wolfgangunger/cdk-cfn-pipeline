from aws_cdk import Stage, DefaultStackSynthesizer
from constructs import Construct

from infrastructure.data.s3bucket_stack import S3Stack





class AppDeploy(Stage):
    def __init__(self, scope: Construct, id: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        # s3 bucket Stack Example
        s3bucket = S3Stack(self, "S3Stack")


