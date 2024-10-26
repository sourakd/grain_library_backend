import pymongo
import pymongo.errors
from settings.configuration import ProductionConfig, DevelopmentConfig

url_mongo_d = DevelopmentConfig.url_mongo
url_mongo_p = ProductionConfig.url_mongo
port_mongo = DevelopmentConfig.port_mongo
db_name_mongo = DevelopmentConfig.db_name_mongo
db_username = ProductionConfig.db_username
db_password = ProductionConfig.db_password

apps = ["development", "production"]
used_app = apps[0]


def get_url():
    if used_app == apps[1]:
        return DevelopmentConfig.url_mongo
    else:
        return ProductionConfig.url_mongo


def connect_mongo_db(url, port):
    try:
        if url == url_mongo_d and port == port_mongo:
            return pymongo.MongoClient(url, port)

        elif url == url_mongo_p and port == port_mongo:
            return pymongo.MongoClient(url, port, username=db_username, password=db_password)
        else:
            return None

    except pymongo.errors.ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None


def connect_database(db_name, db_connect):
    if db_connect:
        try:
            database = db_connect[db_name]
            return database
        except Exception as e:
            print(f"Error accessing database: {e}")
            return None
    else:
        return None


def database_connect_mongo():
    url = get_url()
    port = port_mongo
    conn = connect_mongo_db(url, port)
    if conn:
        db_con = connect_database(db_name_mongo, conn)
        if db_con is not None:
            try:
                status = db_con.command("dbstats")
                print("Database stats:", status)
            except Exception as e:
                print(f"Error getting database stats: {e}")
        return db_con
    return None
