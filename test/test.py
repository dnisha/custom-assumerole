from aws_session_manager import AssumeRoleSessionManager
import os
from EC2ServiceWithRefresh import EC2ServiceWithRefresh

# AWS_ACCESS_KEY_ID='your_access_key'
# AWS_SECRET_ACCESS_KEY='your_secret_key'
# AWS_SESSION_TOKEN='your_session_token'  # Optional
# AWS_ROLE_ARN='arn:aws:iam::370389955750:role/Ec2AssumeRole-Readonly-deepak'

access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
session_token = os.getenv('AWS_TOKEN')
role_arn = os.getenv('AWS_ROLE_ARN')

# session manager object
session_mgr = AssumeRoleSessionManager(
    access_key=access_key,
    secret_key=secret_key,
    session_token=session_token,
    role_arn=role_arn
)

# Assume role for 1 hour (3600 seconds)
# session_mgr.assume_role(duration_seconds=3600)

# Use main flow for service-safe behavior
# creds = session_mgr.main(duration_seconds=3600, threshold_minutes=10, extension_minutes=30)

# # Retrieve credentials and use them
# creds = session_mgr.get_current_credentials()
# print("\n[INFO] Final AWS Credentials:")
# print(creds)

service = EC2ServiceWithRefresh(session_mgr)
response = service.describe_instances()
print(f"all instances {response}")