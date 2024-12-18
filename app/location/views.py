import datetime as dt
import re
from datetime import datetime

import jwt
import pytz
from flask import Blueprint, make_response, jsonify, request, current_app
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError
from passlib.hash import pbkdf2_sha256

from app.location_validation import country_registration_schema, region_registration_schema, \
    sub_region_registration_schema, login_schema
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn

location_add = Blueprint('location_add', __name__)


class AddCountry(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                country = data["country"]
                email_id = data["email_id"].lower()
                password = data["password"]

                if country and email_id and password:

                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "password": password, "country": country, "email_id": email_id}

                    # Validate the data using the schema
                    try:
                        validated_data = country_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        # Hash the password
                        validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    db1.insert_one(validated_data)

                    # Remove the password from the data
                    del validated_data["password"]

                    # Extract the _id value
                    validated_data["_id"] = str(validated_data["_id"])

                    # Create the response
                    response = {"message": "Country added successfully", "status": "success",
                                "data": validated_data}
                    stop_and_check_mongo_status(conn)

                    # Return the response
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class AddRegion(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                country = data["country"]
                region = data["region"]
                email_id = data["email_id"].lower()
                password = data["password"]

                if country and email_id and password and region:

                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "password": password, "country": country, "email_id": email_id, "region": region}

                    # Validate the data using the schema
                    try:
                        validated_data = region_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        # Hash the password
                        validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        db1.insert_one(validated_data)

                        # Remove the password from the data
                        del validated_data["password"]

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])

                        # Create the response
                        response = {"message": "Region added successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)

                        # Return the response
                        return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class AddSubRegion(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                country = data["country"]
                region = data["region"]
                sub_region = data["sub_region"]
                email_id = data["email_id"].lower()
                password = data["password"]

                if country and email_id and password and region and sub_region:

                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "password": password, "country": country, "email_id": email_id, "region": region,
                            "sub_region": sub_region}

                    # Validate the data using the schema
                    try:
                        validated_data = sub_region_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        # Hash the password
                        validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    db1.insert_one(validated_data)

                    # Remove the password from the data
                    del validated_data["password"]

                    # Extract the _id value
                    validated_data["_id"] = str(validated_data["_id"])

                    # Create the response
                    response = {"message": "Sub-region added successfully", "status": "success",
                                "data": validated_data}
                    stop_and_check_mongo_status(conn)

                    # Return the response
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class Login(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                db2 = db["login_token"]
                db2.create_index("expired_at", expireAfterSeconds=0)
                data = request.get_json()
                email_id = data["email_id"].lower()
                password = data["password"]

                if email_id and password:

                    data = {"email_id": email_id, "password": password}

                    # Validate the data using the schema
                    try:
                        login_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        # simpler version to do check {"email_id": {"$regex": "^" + value + "$", "$options": "i"}}{
                        # "email_id": {"$regex": "^" + value + "$", "$options": "i"}}
                        user = db1.find_one(
                            {"$and": [{'email_id': re.compile("^" + re.escape(email_id) + "$", re.IGNORECASE)}],
                             "status": "active"})

                        # Delete the previous token if exists(only single token)
                        db2.delete_many({"e_id": str(user["_id"])})

                        e_token = jwt.encode(
                            {'_id': str(user["_id"]),
                             'exp': datetime.now(pytz.utc) + dt.timedelta(days=7)},
                            current_app.config['SECRET_KEY'], algorithm="HS256")

                        del user["password"]
                        user["_id"] = str(user["_id"])
                        user["token"] = e_token

                        # Save the token into the database
                        db2.insert_one({"e_token": e_token, "e_id": str(user["_id"]),
                                        "created_at": datetime.now(pytz.utc),
                                        "local_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "expired_at": datetime.now(pytz.utc) + dt.timedelta(days=1)})

                        response = {"status": 'success', "data": user, "message": "Login successful"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error',
                                "message": {"Details": ["Email and Password both are required!"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class FetchCountry(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                find_country = db1.find({"status": "active"}, {"country": 1, "_id": 0})
                total_country = db1.count_documents({"status": "active", "country": {"$exists": True}})

                if total_country != 0:
                    country_list = [i["country"] for i in find_country]
                    response = {"status": 'success', "data": country_list, "total_country": total_country,
                                "message": "All country fetched successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"country": ["Please add a country first"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class FetchRegion(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                country = data["country"]
                region = db1.find({"country": country, "status": "active"}, {"region": 1, "_id": 0})
                total_region = db1.count_documents(
                    {"country": country, "status": "active", "region": {"$exists": True}})

                if total_region != 0:
                    region_list = [i["region"] for i in region]
                    response = {"status": 'success', "data": region_list, "total_region": total_region,
                                "message": "All region fetched successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"region": ["Please add a region first"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


class FetchSubRegion(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                country = data["country"]
                region = data["region"]
                sub_region = db1.find({"country": country, "region": region, "status": "active"},
                                      {"sub_region": 1, "_id": 0})
                total_sub_region = db1.count_documents(
                    {"country": country, "region": region, "status": "active", "sub_region": {"$exists": True}})

                if total_sub_region != 0:
                    sub_region_list = [i["sub_region"] for i in sub_region]
                    response = {"status": 'success', "data": sub_region_list, "total_sub_region": total_sub_region,
                                "message": "All sub-region fetched successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"sub_region": ["Please add a sub-region first"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


cnt_add = AddCountry.as_view('cnt_add_view')
reg_add = AddRegion.as_view('reg_add_view')
sub_reg_add = AddSubRegion.as_view('sub_reg_add_view')
login_user = Login.as_view('login_view')
fetch_country = FetchCountry.as_view('fetch_country')
fetch_region = FetchRegion.as_view('fetch_region')
fetch_sub_region = FetchSubRegion.as_view('fetch_sub_region')

location_add.add_url_rule('/location/add_country', view_func=cnt_add, methods=['POST'])
location_add.add_url_rule('/location/add_region', view_func=reg_add, methods=['POST'])
location_add.add_url_rule('/location/add_sub_region', view_func=sub_reg_add, methods=['POST'])
location_add.add_url_rule('/location/login', view_func=login_user, methods=['POST'])
location_add.add_url_rule('/location/fetch_country', view_func=fetch_country, methods=['POST'])
location_add.add_url_rule('/location/fetch_region', view_func=fetch_region, methods=['POST'])
location_add.add_url_rule('/location/fetch_sub_region', view_func=fetch_sub_region, methods=['POST'])
