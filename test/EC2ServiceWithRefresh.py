import boto3
from botocore.exceptions import ClientError  # type: ignore

class EC2ServiceWithRefresh:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self._refresh_client()
    
    def _refresh_client(self):
        creds = self.session_manager.main()
        self.client = boto3.client(
            'ec2',
            aws_access_key_id=creds['aws_access_key_id'],
            aws_secret_access_key=creds['aws_secret_access_key'],
            aws_session_token=creds['aws_session_token'],
            region_name='ap-south-1'
        )
    
    def describe_instances(self):
        try:
            return self.client.describe_instances()
        except ClientError as e: 
            if 'ExpiredToken' in str(e):
                print("Token expired, refreshing...")
                self._refresh_client()
                return self.client.describe_instances()
            raise
