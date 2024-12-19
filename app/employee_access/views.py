import datetime as dt

from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError
from passlib.hash import pbkdf2_sha256

from app.employee_access.employee_validation import employee_registration_schema
from app.helpers import S3Uploader
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn
from settings.configuration import S3Config

employee_access = Blueprint('employee_access', __name__)


class EmployeeRegistration(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                data = dict(request.form)
                employee_name = data["employee_name"]
                email_id = data["email_id"].lower()
                password = data["password"]
                type_id = data["type_id"]
                profile_pic = request.files.get("profile_pic")

                if employee_name and email_id and password and type_id and profile_pic:

                    # emp_schema = EmployeeRegistrationSchema()

                    data = {"status": "active", "type_id": type_id,
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "password": password, "employee_name": employee_name, "email_id": email_id,
                            "profile_pic": profile_pic}

                    # Validate the data using the schema
                    try:
                        validated_data = employee_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # Hash the password
                        validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        s3_config = S3Config()
                        bucket_status, total_files = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        file_url = s3_uploader.upload_file(profile_pic)

                        if s3_uploader.check_existing_file(file_url):
                            response = {"message": "File already exist", "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Insert the data into the database
                        validated_data["profile_pic"] = file_url
                        db1.insert_one(validated_data)

                        # Remove the password from the data
                        del validated_data["password"]

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
                response = {"status": 'val_error', "message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class AllEmployee(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                data = request.get_json()
                type_id = data["type_id"]

                if type_id:
                    find_employee = db1.find({"status": {"$ne": "delete"}, "type_id": type_id}, {"password": 0}).sort(
                        "status", 1)
                    find_employee_list = list(find_employee)
                    total_employee = db1.count_documents({"status": {"$ne": "delete"}, "type_id": type_id})

                    if total_employee != 0:
                        for i in find_employee_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": find_employee_list, "total_employee": total_employee,
                                    "message": "Employee "
                                               "fetched "
                                               "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": 'val_error', "message": {"Employee": ["Please add an employee first"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"DB": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class EmployeeDetails(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                data = request.get_json()
                type_id = data["type_id"]
                employee_id = data["emp_id"]

                if type_id and employee_id:
                    find_employee = db1.find_one(
                        {"status": {"$ne": "delete"}, "type_id": type_id, "_id": ObjectId(employee_id)},
                        {"password": 0})
                    if find_employee:
                        find_employee["_id"] = str(find_employee["_id"])
                        response = {"status": "success", "data": find_employee,
                                    "message": "Employee fetched successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": 'val_error', "message": {"Employee": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"DB": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class EmployeeStatusChange(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                data = request.get_json()
                type_id = data["type_id"]
                employee_id = data["emp_id"]
                emp_status = data["emp_status"]

                if type_id and employee_id and emp_status:

                    current_status = db1.find_one({"type_id": type_id, "_id": ObjectId(employee_id)}, {"status": 1})

                    if current_status is None:
                        response = {"status": 'val_error', "message": {"DB": ["Data not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == "delete":
                        response = {"status": 'val_error',
                                    "message": {"Employee": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == emp_status:
                        response = {"status": 'val_error',
                                    "message": {"Employee": [f"Employee is already {emp_status}"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        update_status = db1.update_one(
                            {"type_id": type_id, "_id": ObjectId(employee_id), "status": {"$ne": "delete"}},
                            {"$set": {"status": emp_status,
                                      "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
                        if update_status.matched_count == 1 and update_status.modified_count == 1:
                            response = {"status": "success", "message": f"Employee {emp_status} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": "error", "message": "Employee not updated"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            else:
                response = {"status": 'val_error', "message": {"DB": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


emp_reg = EmployeeRegistration.as_view('emp_reg_view')
all_emp = AllEmployee.as_view('all_emp_view')
emp_details = EmployeeDetails.as_view('emp_details_view')
emp_status = EmployeeStatusChange.as_view('emp_status_view')

employee_access.add_url_rule('/employee_access/registration', view_func=emp_reg, methods=['POST'])
employee_access.add_url_rule('/employee_access/all_employee', view_func=all_emp, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_details', view_func=emp_details, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_status_change', view_func=emp_status, methods=['POST'])
