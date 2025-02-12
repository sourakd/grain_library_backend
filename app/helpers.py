import datetime as dt
import io
import os
import random
import re
import threading
from functools import wraps

import jwt
from botocore.exceptions import NoCredentialsError
from flask import jsonify, request, current_app

from db_connection import database_connect_mongo


def Admin_Access(U):
    """
    Decorator to check if the user has admin access based on the token in the request headers.
    """

    @wraps(U)
    def wrapper(*args, **kwargs):
        # Get the token from the request headers
        token = request.headers.get('token')

        # Check if the token is valid and not expired
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])

        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token", "status": "val_error"}), 401

        # Connect to the MongoDB database
        db = database_connect_mongo()
        db1 = db["jwt"]

        # Check if the token is active in the database
        if db1.find_one({"token": token, "status": "active"}):
            # Check if the user has admin role
            if decoded_token.get("role_id") == '1':
                # If admin, call the original function
                return U(*args, **kwargs)
            else:
                # If not admin, return an error response
                return jsonify({"message": "unauthorized access", "status": "val_error"}), 401
        else:
            # If the token is not active, return an error response
            return jsonify({"message": "Token is not active", "status": "val_error"}), 401

    return wrapper


class S3Uploader:
    def __init__(self, s3_config):
        self.s3_config = s3_config
        self.s3 = self.s3_config.get_s3_client()
        self.cancel_event = threading.Event()

    def upload_file(self, file, on_progress=None):
        with io.BytesIO(file.read()) as f:
            file_name = str(random.randint(1000, 10000)) + '_' + dt.datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f") + '.' + file.filename.split('.')[-1]
            progress_percentage = ProgressPercentage(file, on_progress, self.cancel_event)
            try:
                self.s3.upload_fileobj(f, self.s3_config.get_bucket_name(), file_name,
                                       ExtraArgs={'ContentDisposition': 'inline', 'ContentType': file.content_type},
                                       Callback=progress_percentage)
            except Exception as e:
                if self.cancel_event.is_set():
                    self.s3.delete_object(Bucket=self.s3_config.get_bucket_name(), Key=file_name)
                    raise Exception("Upload cancelled")
                else:
                    raise e

            file_url = f"https://{self.s3_config.get_bucket_name()}.s3.{self.s3_config.get_region_name()}.amazonaws.com/{file_name}"
            return {'file_url': file_url, 'progress': f"{progress_percentage.get_progress()}%"}

    def cancel_upload(self, file_url):
        self.cancel_event.set()
        file_name = file_url.split('/')[-1]
        try:
            self.s3.delete_object(Bucket=self.s3_config.get_bucket_name(), Key=file_name)
        except NoCredentialsError:
            print("Credentials not available")
        except Exception as e:
            raise e

    def check_existing_file(self, file_url):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.find_one({"$and": [{'file': re.compile("^" + re.escape(file_url) + "$", re.IGNORECASE)}]}):
            return True
        return False

    def check_existing_file_story(self, file_urls):
        db = database_connect_mongo()
        db1 = db["story"]
        for file_url_dict in file_urls:
            file_url = file_url_dict['file_url']
            if db1.find_one({"$and": [{'file': re.compile("^" + re.escape(file_url) + "$", re.IGNORECASE)}]}):
                return True
        return False


class ProgressPercentage(object):
    def __init__(self, file, on_progress=None, cancel_event=None):
        self._file = file
        self._seen_so_far = 0
        self._total_size = os.fstat(file.fileno()).st_size
        self._lock = threading.Lock()
        self._on_progress = on_progress
        self._progress = 0
        self._cancel_event = cancel_event

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            self._progress = (self._seen_so_far / self._total_size) * 100
            if self._cancel_event.is_set():
                raise Exception("Upload cancelled")
            if self._on_progress:
                self._on_progress(self._progress)
            print(f"\r{self._progress:.2f}%")

    def get_progress(self):
        return self._progress
