import json

import boto3
import botocore

with open('settings\\keys.json', 'r') as file:
    config_keys = json.load(file)


class Config:
    USER_SECRET_KEY = config_keys['USER_SECRET_KEY']
    ADMIN_SECRET_KEY = config_keys['ADMIN_SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = config_keys['DATABASE_URI']


class S3Config:
    def __init__(self):
        self.bucket_name = config_keys['bucket_name']
        self.access_key = config_keys['aws_access_key_id']
        self.secret_key = config_keys['aws_secret_access_key']
        self.region_name = config_keys['region_name']

    def get_s3_client(self):
        try:
            return boto3.client('s3', aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key,
                                region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            print("Error: No AWS credentials found.")
            return None
        except Exception as e:
            print(f"Error creating S3 client: {str(e)}")
            return None

    def get_bucket_name(self):
        return self.bucket_name

    def get_region_name(self):
        return self.region_name

    def get_bucket_status(self):
        s3 = self.get_s3_client()
        if s3 is None:
            return "Error: Unable to create S3 client."
        try:
            s3.head_bucket(Bucket=self.bucket_name)
            return "Bucket exists and is accessible"
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return "Bucket not found."
            else:
                return f"Error accessing bucket: {str(e)}"
        except Exception as e:
            return f"Error accessing bucket: {str(e)}"

    def get_total_files(self):
        s3 = self.get_s3_client()
        if s3 is None:
            return "Error: Unable to create S3 client."
        try:
            response = s3.list_objects_v2(Bucket=self.bucket_name)
            return response['KeyCount']
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return "Bucket not found."
            else:
                return f"Error listing objects: {str(e)}"
        except Exception as e:
            return f"Error listing objects: {str(e)}"

    def connect_to_s3(self):
        print(f"Connecting to S3 bucket {self.bucket_name}...")
        bucket_status = self.get_bucket_status()
        total_files = self.get_total_files()
        print(f"S3 bucket status: {bucket_status}")
        print(f"Total files in S3 bucket: {total_files}")
        return bucket_status, total_files


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = config_keys['SECRET_KEY']
    url_mongo = config_keys['MONGO_URL'][0]
    port_mongo = config_keys['PORT_MONGO']
    db_name_mongo = config_keys['DB_NAME_MONGO']


class ProductionConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = config_keys['SECRET_KEY']
    url_mongo = config_keys['MONGO_URL'][1]
    port_mongo = config_keys['PORT_MONGO']
    db_name_mongo = config_keys['DB_NAME_MONGO']
    db_username = config_keys['DB_USERNAME']
    db_password = config_keys['DB_PASSWORD']


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
