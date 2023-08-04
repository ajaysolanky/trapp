import datetime
import logging
import os
import threading
import time
import boto3
import multiprocessing
from botocore.config import Config
# from firebase_admin import storage
from abc import ABC, abstractmethod
import mimetypes

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID_VAR')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY_VAR')

DL_LINK_VALID_SECONDS = 60*60*24*30

NUM_UPLOAD_ATTEMPTS = 3
UPLOAD_TIMEOUT = 3

def get_content_type(file_path):
    return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

class FileUploader(ABC):
    def __init__(self):
        self.client = self.init_client()
    
    def init_client(self):
        raise NotImplementedError()
    
    @abstractmethod
    def upload(self, file_path, target_file_name):
        """Upload a file to remote storage

        :param file_path: path to file to upload
        :param target_file_name: file name to upload to
        :return: url to object
        """
        pass

class S3Uploader(FileUploader):
    def __init__(self):
        self.client = None
        self.client_fetch_thread = self.get_s3_client_async()

    def get_s3_client_async(self):
        t = threading.Thread(target=self.set_client)
        t.start()
        return t

    def set_client(self):
        # TODO: use the S3 retries instead of this janky for loop
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=Config(connect_timeout=UPLOAD_TIMEOUT,retries={'max_attempts': 0})
            )
        self.client = s3_resource.meta.client

    def upload(self, file_path, target_file_name):
        st = time.time()
        if self.client_fetch_thread.is_alive():
            self.client.fetch_thread.join()
        content_type = get_content_type(file_path)
        extra_args = {'ContentType': content_type, 'ContentDisposition': 'inline'}
        BUCKET_NAME = 'trapp-files'
        upload_fn = lambda: self.client.upload_file(file_path, BUCKET_NAME, target_file_name, ExtraArgs=extra_args)
        upload_successful = False
        #TODO: make sure this actually works
        for i in range(NUM_UPLOAD_ATTEMPTS):
            try:
                upload_fn()
                upload_successful = True
                break
            except:
                logging.warning(f"Upload attempt {i} failed")
        if not upload_successful:
            raise Exception("Upload failed")
        # self.client.upload_file(file_path, BUCKET_NAME, target_file_name)
        url = self.client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': BUCKET_NAME, 'Key': target_file_name}, ExpiresIn=DL_LINK_VALID_SECONDS)
        return url

S3UploaderObj = S3Uploader()

# class GoogleStorageUploader(FileUploader):
#     def init_client(self):
#         return storage.bucket()
    
#     def upload(self, file_path, target_file_name):
#         blob = self.client.blob(target_file_name)
#         blob.upload_from_filename(file_path)
#         return blob.generate_signed_url(datetime.timedelta(seconds=DL_LINK_VALID_SECONDS), method='GET')
