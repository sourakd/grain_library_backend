import json

with open('settings\keys.json', 'r') as file:
    config_keys = json.load(file)


class Config:
    USER_SECRET_KEY = config_keys['USER_SECRET_KEY']
    ADMIN_SECRET_KEY = config_keys['ADMIN_SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = config_keys['DATABASE_URI']


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
