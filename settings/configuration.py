import json

import boto3

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
        print(self.access_key)

    def get_s3_client(self):
        return boto3.client('s3', aws_access_key_id=self.access_key,
                            aws_secret_access_key=self.secret_key,
                            region_name=self.region_name)

    def get_bucket_name(self):
        return self.bucket_name

    def get_region_name(self):
        return self.region_name


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
