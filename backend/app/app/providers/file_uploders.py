import abc
import asyncio

import boto3
from botocore.exceptions import NoCredentialsError


class FileUploader(abc.ABC):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    @abc.abstractmethod
    async def save_file_async(self, file, file_name):
        raise NotImplementedError


class S3FileUploader(FileUploader):
    def __init__(self, bucket_name, access_key_id, secret_access_key, region_name):
        self.bucket_name = bucket_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_name = region_name

    async def save_file_async(self, file, file_name):
        s3 = boto3.client('s3',
                          aws_access_key_id=self.access_key_id,
                          aws_secret_access_key=self.secret_access_key,
                          region_name=self.region_name)
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3.upload_fileobj,
                file,
                self.bucket_name,
                file_name
            )
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_name}"
        except NoCredentialsError:
            return None


