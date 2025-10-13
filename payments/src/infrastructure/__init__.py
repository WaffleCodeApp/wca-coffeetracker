import os
from .parameters import ParametersWithSSM
from .id_token import IdTokenWithJose


async def initialize() -> None:
    await ParametersWithSSM.set_environment(
        aws_region=os.getenv("AWS_REGION"), deployment_id=os.getenv("DEPLOYMENT_ID")
    )
    ParametersWithSSM.get_cognito_client_id()
    await IdTokenWithJose.set_environment(
        aws_region=os.getenv("AWS_REGION"),
        deployment_id=os.getenv("DEPLOYMENT_ID"),
        cognito_region=await ParametersWithSSM.get_cognito_region(),
        cognito_user_pool_id=await ParametersWithSSM.get_congito_user_pool_id(),
        cognito_client_id=await ParametersWithSSM.get_cognito_client_id(),
    )
