import boto3
import datetime
import logging
from dateutil.tz import tzutc

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#initial setup with the temporary credentials and role in order to setup a new session
class AssumeRoleSessionManager:
    def __init__(self, access_key, secret_key, session_token, role_arn, session_name='UserSession'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.role_arn = role_arn
        self.session_name = session_name

        self.sts_client = boto3.client(
            'sts',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token
        )

        self.credentials = None
        self.expiration = None

    #assumes a role and gets new temporary credentials 
    def assume_role(self, duration_seconds=3600):
        response = self.sts_client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=duration_seconds
        )
        creds = response['Credentials']
        self.credentials = {
            'aws_access_key_id': creds['AccessKeyId'],
            'aws_secret_access_key': creds['SecretAccessKey'],
            'aws_session_token': creds['SessionToken']
        }
        self.expiration = creds['Expiration']
        logger.info(f"Session assumed. Credentials will expire at {self.expiration}")
        return self.credentials

    #warns if the session is expiring 
    def check_if_session_expiring(self, threshold_minutes=10):
        if not self.expiration:
            logger.warning("No active session found.")
            return False

        now = datetime.datetime.now(tzutc())
        minutes_left = (self.expiration - now).total_seconds() / 60
        logger.info(f"Time left in session: {int(minutes_left)} minutes")
        return minutes_left < threshold_minutes

    #background-service
    def main(self, duration_seconds=3600, threshold_minutes=10, extension_minutes=30):
        """
        Main service-safe entry point.
        Automatically assumes/extends session without user input.
        """
        self.assume_role(duration_seconds=duration_seconds)

        if self.check_if_session_expiring(threshold_minutes=threshold_minutes):
            logger.info(f"Session expiring soon. Auto-extending by {extension_minutes} minutes.")
            self.assume_role(duration_seconds=extension_minutes * 60)

        return self.get_current_credentials()

    #returns the current credentials for the user to use
    def get_current_credentials(self):
        if self.credentials:
            return self.credentials
        else:
            logger.info("No credentials available. Please run assume_role first.")
            return None