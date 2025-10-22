import boto3
import json
from functools import lru_cache
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self, secret_name="marsh-backend/all-secrets", region_name="ap-southeast-1"):
        self.secret_name = secret_name
        self.region_name = region_name
        
        # Create a Secrets Manager client
        session = boto3.session.Session()
        self.client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
    
    @lru_cache(maxsize=1)  # Cache the secret for performance
    def get_all_secrets(self) -> dict:
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.secret_name
            )
            secret = get_secret_value_response['SecretString']
            
            # Parse the JSON secret
            return json.loads(secret)
            
        except ClientError as e:
            # Handle specific AWS errors
            error_code = e.response['Error']['Code']
            if error_code == 'DecryptionFailureException':
                raise Exception("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            elif error_code == 'InternalServiceErrorException':
                raise Exception("An error occurred on the server side.")
            elif error_code == 'InvalidParameterException':
                raise Exception("You provided an invalid value for a parameter.")
            elif error_code == 'InvalidRequestException':
                raise Exception("You provided a parameter value that is not valid for the current state of the resource.")
            elif error_code == 'ResourceNotFoundException':
                raise Exception(f"We can't find the secret '{self.secret_name}' that you asked for.")
            else:
                raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def get_secret_value(self, key: str) -> str:
        secrets = self.get_all_secrets()
        if key not in secrets:
            available_keys = list(secrets.keys())
            raise Exception(f"Secret key '{key}' not found. Available keys: {available_keys}")
        return secrets[key]

# Global instance
secrets_manager = SecretsManager()

# Helper functions for all your variables
def get_mongo_url():
    return secrets_manager.get_secret_value("MONGO_URL")

def get_tavily_api_key():
    return secrets_manager.get_secret_value("TAVILY_API_KEY")

def get_openai_api_key():
    return secrets_manager.get_secret_value("OPENAI_API_KEY")

def get_phoenix_api_key():
    return secrets_manager.get_secret_value("PHOENIX_API_KEY")

def get_otel_exporter_otlp_headers():
    return secrets_manager.get_secret_value("OTEL_EXPORTER_OTLP_HEADERS")

def get_logo_dev_token():
    return secrets_manager.get_secret_value("LOGO_DEV_TOKEN")

def get_aws_access_key_id():
    return secrets_manager.get_secret_value("AWS_ACCESS_KEY_ID")

def get_aws_secret_access_key():
    return secrets_manager.get_secret_value("AWS_SECRET_ACCESS_KEY")

def get_s3_bucket_name():
    return secrets_manager.get_secret_value("S3_BUCKET_NAME")

def get_s3_region():
    return secrets_manager.get_secret_value("S3_REGION")

def get_template_s3_key():
    return secrets_manager.get_secret_value("TEMPLATE_S3_KEY")

# Test function
def test_secrets():
    """Test function to verify all secrets can be retrieved"""
    try:
        secrets = secrets_manager.get_all_secrets()
        print(f"Found {len(secrets)} secrets")
        return True
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        return False

if __name__ == "__main__":
    # Test the secrets when running this file directly
    test_secrets()