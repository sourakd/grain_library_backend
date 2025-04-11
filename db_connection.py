import time

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
used_app = apps[1]


def get_url():
    if used_app == apps[0]:
        return url_mongo_d
    else:
        return url_mongo_p


def connect_mongo_db(url, port, timeout_ms=5000):
    max_retries = 3
    retry_delay = 1  # second

    for attempt in range(max_retries):
        try:
            if url == url_mongo_d and port == port_mongo:
                return pymongo.MongoClient(url, port, serverSelectionTimeoutMS=timeout_ms)

            elif url == url_mongo_p and port == port_mongo:
                return pymongo.MongoClient(url, port, username=db_username, password=db_password,
                                           serverSelectionTimeoutMS=timeout_ms)
            else:
                return None

        except pymongo.errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"Connection timeout error (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

    print("Failed to connect to MongoDB after {} attempts".format(max_retries))
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


def database_connect_mongo(timeout_ms=5000):
    url = get_url()
    port = port_mongo
    conn = connect_mongo_db(url, port, timeout_ms=timeout_ms)
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


def start_and_check_mongo(timeout_ms=5000):
    url = get_url()
    port = port_mongo
    try:
        conn = pymongo.MongoClient(url, port, serverSelectionTimeoutMS=timeout_ms, socketTimeoutMS=5000)
        conn.admin.command('ping')
        print("MongoDB connection established and server is running")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Failed to establish MongoDB connection or server is not running")
        return None


def stop_and_check_mongo_status(conn):
    if conn:
        try:
            conn.close()
            print("MongoDB connection closed")
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")
    url = get_url()
    try:
        client = pymongo.MongoClient(url, port_mongo)
        client.admin.command('ping')
        print("MongoDB server is running")
    except pymongo.errors.ConnectionFailure as e:
        print("MongoDB server is not running")
    finally:
        client.close()


conn = start_and_check_mongo(timeout_ms=5000)
db = database_connect_mongo(timeout_ms=5000)
# Perform operations on the database
stop_and_check_mongo_status(conn)
