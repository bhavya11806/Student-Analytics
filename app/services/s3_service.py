import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from flask import current_app

class S3Service:
    def __init__(self):
        self._s3_client = None

    def _get_client(self):
        if self._s3_client is not None:
            return self._s3_client

        region = current_app.config.get("AWS_REGION", "ap-south-1")
        access_key = current_app.config.get("AWS_ACCESS_KEY_ID")
        secret_key = current_app.config.get("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            self._s3_client = boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        else:
            # Attempt default IAM credentials (for EC2 / Lambda environment)
            try:
                self._s3_client = boto3.client("s3", region_name=region)
            except Exception:
                self._s3_client = None

        return self._s3_client

    def is_configured(self) -> bool:
        bucket = current_app.config.get("AWS_S3_BUCKET_NAME")
        if not bucket:
            return False
        client = self._get_client()
        return client is not None

    def upload_file(self, local_path: str, s3_key: str, content_type: str = None) -> tuple[bool, str]:
        """
        Uploads a file to Amazon S3. If S3 is not configured or fails,
        returns (False, local_path) so the application functions locally.
        """
        bucket = current_app.config.get("AWS_S3_BUCKET_NAME")
        if not bucket:
            return False, "S3 bucket name not configured. Stored locally."

        client = self._get_client()
        if not client:
            return False, "AWS credentials not available. Stored locally."

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            client.upload_file(local_path, bucket, s3_key, ExtraArgs=extra_args)
            return True, f"s3://{bucket}/{s3_key}"
        except (ClientError, NoCredentialsError) as e:
            return False, str(e)

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str | None:
        """
        Generates a secure temporary presigned download URL for a private S3 object.
        Never makes sensitive academic records publicly accessible.
        """
        bucket = current_app.config.get("AWS_S3_BUCKET_NAME")
        client = self._get_client()
        if not bucket or not client:
            return None

        try:
            url = client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError:
            return None

s3_service = S3Service()
