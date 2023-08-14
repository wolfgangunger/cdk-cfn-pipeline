from constructs import Construct
from aws_cdk import (
    Stack,
)
from infrastructure.iam.bootstrap_role_construct import BootstrapRole


class BootstrapRoleStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        toolchain_account: str,
        stage: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        BootstrapRole(
            self,
            f"{stage}-role",
            toolchain_account,
            stage
        )
