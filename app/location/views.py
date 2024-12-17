import datetime as dt

from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError
from passlib.hash import pbkdf2_sha256

from app.location_validation import country_registration_schema, region_registration_schema, \
    sub_region_registration_schema
from db_connection import *

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


cnt_add = AddCountry.as_view('cnt_add_view')
reg_add = AddRegion.as_view('reg_add_view')
sub_reg_add = AddSubRegion.as_view('sub_reg_add_view')

location_add.add_url_rule('/location/country_add', view_func=cnt_add, methods=['POST'])
location_add.add_url_rule('/location/region_add', view_func=reg_add, methods=['POST'])
location_add.add_url_rule('/location/sub_region_add', view_func=sub_reg_add, methods=['POST'])
