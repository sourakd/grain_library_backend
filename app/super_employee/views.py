import datetime as dt
import re
from datetime import datetime

import jwt
import pytz
from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request, current_app
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError
from passlib.hash import pbkdf2_sha256

from app.employee_access.employee_validation import employee_registration_schema
from app.helpers import S3Uploader
from app.location.location_validation import country_registration_schema
from app.super_employee.super_employee_validation import super_employee_login_schema
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn
from settings.configuration import S3Config

super_employee_access = Blueprint('super_employee_access', __name__)


class SuperEmployeeRegistration(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["super_employee"]
                data = dict(request.form)
                employee_name = data["employee_name"]
                email_id = data["email_id"].lower()
                address = data["address"]
                id_proof = data["id_proof"].lower()
                phone_number = data["phone_number"]
                type_id = data["type_id"]
                id_no = data["id_no"]
                profile_pic = request.files.get("profile_pic")

                if employee_name and email_id and phone_number and profile_pic and address and id_proof and id_no:

                    # emp_schema = EmployeeRegistrationSchema()

                    data = {"status": "active", "type_id": type_id,
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "employee_name": employee_name, "email_id": email_id,
                            "address": address, "id_proof": id_proof, "id_no": id_no,
                            "phone_number": phone_number, "profile_pic": profile_pic}

                    # Validate the data using the schema
                    try:
                        validated_data = employee_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        validated_data["loc_assign"] = "false"
                        validated_data["type_id"] = "super_admin"

                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        file_url = s3_uploader.upload_file(profile_pic)

                        if s3_uploader.check_existing_file(file_url['file_url'], type_id):
                            response = {"message": "File already exist", "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Insert the data into the database
                        validated_data["profile_pic"] = file_url
                        db1.insert_one(validated_data)

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])

                        # Create the response
                        response = {"message": "Employee registration successful", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)

                        # Return the response
                        return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class AddSuperLocation(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["super_location"]
                data = request.get_json()
                location = data["location"].lower()
                email_id = data["email_id"].lower()
                password = data["password"]

                if email_id and password:

                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "password": password, "location": location, "email_id": email_id,
                            "emp_assign": "false"}

                    # Validate the data using the schema
                    try:
                        validated_data = country_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:

                        # Hash the password
                        validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        # Add type
                        validated_data["type_id"] = "super_location"

                    db1.insert_one(validated_data)

                    # Remove the password from the data
                    del validated_data["password"]

                    # Extract the _id value
                    validated_data["_id"] = str(validated_data["_id"])

                    # Create the response
                    response = {"message": "Super location added successfully", "status": "success",
                                "data": validated_data}
                    stop_and_check_mongo_status(conn)

                    # Return the response
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class SuperLogin(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["super_location"]
                db2 = db["login_token"]
                db3 = db["super_employee"]
                db2.create_index("expired_at", expireAfterSeconds=0)
                data = request.get_json()
                email_id = data["email_id"].lower()
                password = data["password"]

                if email_id and password:

                    data = {"email_id": email_id, "password": password}

                    # Validate the data using the schema
                    try:
                        super_employee_login_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # simpler version to do check {"email_id": {"$regex": "^" + value + "$", "$options": "i"}}{
                        # "email_id": {"$regex": "^" + value + "$", "$options": "i"}}
                        location = db1.find_one(
                            {"$and": [{'email_id': re.compile("^" + re.escape(email_id) + "$", re.IGNORECASE)}],
                             "status": "active"})

                        emp_id = location.get("s_e_id", "Employee not assign")

                        employee = db3.find_one({"_id": ObjectId(emp_id), "status": "active"})

                        if not employee:
                            response = {"status": 'val_error',
                                        "message": {"Details": ["Employee not found"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Delete the previous token if exists(only single token)
                        db2.delete_many({"e_id": str(location["_id"])})

                        s_token = jwt.encode(
                            {'_id': str(location["_id"]),
                             'exp': datetime.now(pytz.utc) + dt.timedelta(days=7)},
                            current_app.config['SECRET_KEY'], algorithm="HS256")

                        del location["password"]
                        location["_id"] = str(location["_id"])
                        location["token"] = s_token
                        location["profile_pic"] = employee["profile_pic"]["file_url"]
                        location["employee_name"] = employee["employee_name"]
                        location["employee_email"] = employee["email_id"]
                        location["employee_designation"] = employee["type_id"]

                        # Save the token into the database
                        db2.insert_one({"s_token": s_token, "s_id": str(location["_id"]),
                                        "created_at": datetime.now(pytz.utc),
                                        "local_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "expired_at": datetime.now(pytz.utc) + dt.timedelta(days=1)})

                        response = {"status": 'success', "data": location, "message": "Login successful"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error',
                                "message": {"Details": ["Email and Password both are required!"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class AssignSuperEmployee(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["super_location"]
                db2 = db["super_employee"]
                data = request.get_json()
                s_l_id = data["s_l_id"]
                s_e_id = data["s_e_id"]

                if not s_l_id and s_e_id:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

                find_s_l = db1.find_one({"_id": ObjectId(s_l_id), "status": "active"})
                find_s_e = db2.find_one({"_id": ObjectId(s_e_id), "status": "active"})

                if not find_s_l or not find_s_e:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter valid details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

                else:
                    db1.update_one({"_id": ObjectId(s_l_id)}, {"$set": {"emp_assign": "true"}})
                    db2.update_one({"_id": ObjectId(s_e_id)}, {"$set": {"s_l_id": s_l_id}})
                    db2.update_one({"_id": ObjectId(s_e_id)}, {"$set": {"loc_assign": "true"}})
                    db1.update_one({"_id": ObjectId(s_l_id)}, {"$set": {"s_e_id": s_e_id}})
                    response = {"status": 'success', "message": "Employee assigned successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


s_emp_reg = SuperEmployeeRegistration.as_view('s_emp_reg_view')
s_loc_reg = AddSuperLocation.as_view('s_loc_reg_view')
s_login = SuperLogin.as_view('s_login_view')
s_emp_assign = AssignSuperEmployee.as_view('s_emp_assign_view')

super_employee_access.add_url_rule('/super_employee_access/registration', view_func=s_emp_reg, methods=['POST'])
super_employee_access.add_url_rule('/super_employee_access/add_location', view_func=s_loc_reg, methods=['POST'])
super_employee_access.add_url_rule('/super_employee_access/login', view_func=s_login, methods=['POST'])
super_employee_access.add_url_rule('/super_employee_access/assign_super_employee', view_func=s_emp_assign,
                                   methods=['POST'])
