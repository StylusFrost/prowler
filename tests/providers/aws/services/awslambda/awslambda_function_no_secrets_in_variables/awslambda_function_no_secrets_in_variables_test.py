from unittest import mock

from prowler.providers.aws.services.awslambda.awslambda_service import Function
from tests.providers.aws.utils import (
    AWS_ACCOUNT_NUMBER,
    AWS_REGION_US_EAST_1,
    set_mocked_aws_provider,
)


class Test_awslambda_function_no_secrets_in_variables:
    def test_no_functions(self):
        lambda_client = mock.MagicMock
        lambda_client.functions = {}
        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 0

    def test_function_no_variables(self):
        lambda_client = mock.MagicMock
        function_name = "test-lambda"
        function_runtime = "nodejs4.3"
        function_arn = f"arn:aws:lambda:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:function/{function_name}"
        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        lambda_client.functions = {
            "function_name": Function(
                name=function_name,
                security_groups=[],
                arn=function_arn,
                region=AWS_REGION_US_EAST_1,
                runtime=function_runtime,
            )
        }

        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_id == function_name
            assert result[0].resource_arn == function_arn
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"No secrets found in Lambda function {function_name} variables."
            )
            assert result[0].resource_tags == []

    def test_function_secrets_in_keyword(self):
        lambda_client = mock.MagicMock
        function_name = "test-lambda"
        function_runtime = "nodejs4.3"
        function_arn = f"arn:aws:lambda:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:function/{function_name}"

        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        lambda_client.functions = {
            "function_name": Function(
                name=function_name,
                security_groups=[],
                arn=function_arn,
                region=AWS_REGION_US_EAST_1,
                runtime=function_runtime,
                environment={"db_password": "test-password"},
            )
        }

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_id == function_name
            assert result[0].resource_arn == function_arn
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Potential secret found in Lambda function {function_name} variables -> Secret Keyword in variable db_password."
            )
            assert result[0].resource_tags == []

    def test_function_secrets_in_keyword_and_variable(self):
        lambda_client = mock.MagicMock
        function_name = "test-lambda"
        function_runtime = "nodejs4.3"
        function_arn = f"arn:aws:lambda:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:function/{function_name}"

        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        lambda_client.functions = {
            "function_name": Function(
                name=function_name,
                security_groups=[],
                arn=function_arn,
                region=AWS_REGION_US_EAST_1,
                runtime=function_runtime,
                environment={"db_password": "srv://admin:pass@db"},
            )
        }

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_id == function_name
            assert result[0].resource_arn == function_arn
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Potential secret found in Lambda function {function_name} variables -> Secret Keyword in variable db_password, Basic Auth Credentials in variable db_password."
            )
            assert result[0].resource_tags == []

    def test_function_secrets_in_variables_telegram_token(self):
        lambda_client = mock.MagicMock
        function_name = "test-lambda"
        function_runtime = "nodejs4.3"
        function_arn = f"arn:aws:lambda:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:function/{function_name}"
        lambda_client.audit_config = {"secrets_ignore_patterns": []}
        lambda_client.functions = {
            "function_name": Function(
                name=function_name,
                security_groups=[],
                arn=function_arn,
                region=AWS_REGION_US_EAST_1,
                runtime=function_runtime,
                environment={"TELEGRAM_BOT_TOKEN": "telegram-token"},
            )
        }

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_id == function_name
            assert result[0].resource_arn == function_arn
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"No secrets found in Lambda function {function_name} variables."
            )
            assert result[0].resource_tags == []

    def test_function_no_secrets_in_variables(self):
        lambda_client = mock.MagicMock
        function_name = "test-lambda"
        function_runtime = "nodejs4.3"
        function_arn = f"arn:aws:lambda:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:function/{function_name}"
        lambda_client.audit_config = {"secrets_ignore_patterns": []}

        lambda_client.functions = {
            "function_name": Function(
                name=function_name,
                security_groups=[],
                arn=function_arn,
                region=AWS_REGION_US_EAST_1,
                runtime=function_runtime,
                environment={"db_username": "test-user"},
            )
        }

        with (
            mock.patch(
                "prowler.providers.common.provider.Provider.get_global_provider",
                return_value=set_mocked_aws_provider(),
            ),
            mock.patch(
                "prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables.awslambda_client",
                new=lambda_client,
            ),
        ):
            # Test Check
            from prowler.providers.aws.services.awslambda.awslambda_function_no_secrets_in_variables.awslambda_function_no_secrets_in_variables import (
                awslambda_function_no_secrets_in_variables,
            )

            check = awslambda_function_no_secrets_in_variables()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_id == function_name
            assert result[0].resource_arn == function_arn
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"No secrets found in Lambda function {function_name} variables."
            )
            assert result[0].resource_tags == []
