import asyncio
import functools
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
from botocore.exceptions import ClientError  # pyright: ignore[reportMissingTypeStubs]


class ParametersWithSSM:
    _aws_region: str = "us-east-1"
    _deployment_id: str = ""

    _ssm_client: Any | None = None

    @classmethod
    def set_environment(
        cls,
        aws_region: str | None,
        deployment_id: str | None,
    ):
        if aws_region is None:
            print(
                "ParametersWithSSM::initialize: aws_region is None, probably an issue with the env vars"
            )
            raise Exception("aws_region is None")
        cls._aws_region = aws_region
        if deployment_id is None:
            print(
                "ParametersWithSSM::initialize: deployment_id is None, probably an issue with the env vars"
            )
            raise Exception("deployment_id is None")
        cls._deployment_id = deployment_id

    @classmethod
    async def initialize(cls) -> None:
        await cls._get_client()

    @classmethod
    async def _get_client(cls) -> Any:
        if cls._ssm_client is None:
            session_kw = {}
            session = Session(**session_kw)  # type: ignore
            loop = asyncio.get_running_loop()
            cls._ssm_client = await loop.run_in_executor(
                None,
                functools.partial(
                    session.client,  # type: ignore
                    "ssm",
                    region_name=cls._aws_region,
                ),
            )
        return cls._ssm_client

    @classmethod
    async def get_ecs_alb_url(cls, pipeline_id: str) -> str | None:
        client = await cls._get_client()
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.get_parameter,
                    Name=f"/{cls._deployment_id}/ecs/{pipeline_id}/albDnsName",
                ),
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ParameterNotFound":  # type: ignore
                print(
                    f"ParametersWithSSM::get_ecs_alb_url: WARNING, value not found deployment_id {cls._deployment_id}"
                )
                return None
            else:
                raise ex
        else:
            assert isinstance(response["Parameter"]["Value"], str)
            return response["Parameter"]["Value"]

    @classmethod
    async def get_congito_user_pool_id(cls) -> str | None:
        client = await cls._get_client()
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.get_parameter,
                    Name=f"/{cls._deployment_id}/auth/user_pool_ref",
                ),
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ParameterNotFound":  # type: ignore
                print(
                    f"ParametersWithSSM::get_congito_user_pool_id: WARNING, value not found deployment_id {cls._deployment_id}"
                )
                return None
            else:
                raise ex
        else:
            assert isinstance(response["Parameter"]["Value"], str)
            return response["Parameter"]["Value"]

    @classmethod
    async def get_cognito_client_id(cls, pipeline_id: str) -> str | None:
        client = await cls._get_client()
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.get_parameter,
                    Name=f"/{cls._deployment_id}/cdn/{pipeline_id}/auth_user_pool_client_id",
                ),
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ParameterNotFound":  # type: ignore
                print(
                    f"ParametersWithSSM::get_cognito_client_id: WARNING, value not found deployment_id {cls._deployment_id}"
                )
                return None
            else:
                raise ex
        else:
            assert isinstance(response["Parameter"]["Value"], str)
            return response["Parameter"]["Value"]

    @classmethod
    async def get_lambda_arn(cls, pipeline_id: str) -> str | None:
        client = await cls._get_client()
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.get_parameter,
                    Name=f"/{cls._deployment_id}/lambda/{pipeline_id}/arn",
                ),
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ParameterNotFound":  # type: ignore
                print(
                    f"ParametersWithSSM::get_lambda_arn: WARNING, value not found deployment_id {cls._deployment_id}, pipeline_id {pipeline_id}"
                )
                return None
            else:
                raise ex
        else:
            assert isinstance(response["Parameter"]["Value"], str)
            return response["Parameter"]["Value"]
