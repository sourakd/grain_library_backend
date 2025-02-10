import datetime as dt

from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError

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
                employee_name = data["employee_name"].lower()
                email_id = data["email_id"].lower()
                type_id = data["type_id"].lower()
                address = data["address"].lower()
                id_proof = data["id_proof"].lower()
                phone_number = data["phone_number"]
                id_no = data["id_no"]
                profile_pic = request.files.get("profile_pic")

                if employee_name and email_id and phone_number and type_id and profile_pic and address and id_proof and id_no:

                    # emp_schema = EmployeeRegistrationSchema()

                    data = {"status": "active", "type_id": type_id,
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "employee_name": employee_name, "email_id": email_id,
                            "address": address, "id_proof": id_proof, "id_no": id_no,
                            "phone_number": phone_number,
                            "profile_pic": profile_pic}

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
                        validated_data["loc_assign"] = "false"
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
                assign = data["assign"]

                if type_id and assign is None or assign == "":
                    find_employee = db1.find({"status": {"$ne": "delete"}, "type_id": type_id},
                                             {"password": 0}).sort("status", 1)
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

                if type_id and assign:
                    print("Please")
                    find_employee = db1.find({"status": {"$ne": "delete"}, "type_id": type_id, "loc_assign": assign},
                                             {"password": 0}).sort(
                        "status", 1)
                    find_employee_list = list(find_employee)
                    total_employee = db1.count_documents(
                        {"status": {"$ne": "delete"}, "type_id": type_id, "loc_assign": assign})

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
                    response = {"status": 'val_error', "message": {"Details": ["Please enter type ID"]}}
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


class AdminAssign(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                db2 = db["location"]
                data = request.get_json()
                employee_id = data["emp_id"]
                location_id = data["loc_id"]

                if employee_id and location_id:

                    employee = db1.find_one({"_id": ObjectId(employee_id), "status": "active", "type_id": "admin"})

                    location = db2.find_one({"_id": ObjectId(location_id), "status": "active", "type_id": "country"})

                    if employee is None:
                        response = {"status": 'val_error', "message": {"Details": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if location is None:
                        response = {"status": 'val_error', "message": {"Details": ["Location not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        employee_name = employee.get("employee_name", None)
                        employee_assign = employee.get("assign", None)
                        employee_type = employee.get("type_id", None)
                        location_name = location.get("location", None)
                        location_assign = location.get("assign", None)
                        location_type = location.get("type_id", None)

                        if employee_type != "admin" or location_type != "country":
                            response = {"status": 'val_error', "message": {"Details": ["Only admin assign to country"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if employee_assign == "true":
                            location = employee["location"]
                            response = {"status": 'val_error', "message": {"Employee": [f"{employee_name} is already "
                                                                                        f"assign to {location}"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if location_assign == "true":
                            employee = location["employee"]
                            response = {"status": 'val_error', "message": {"Country": [f"{location_name} is already "
                                                                                       f"assign with {employee}"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        else:
                            db1.update_one({"_id": ObjectId(employee_id)},
                                           {"$set": {"location": location_name, "loc_id": location_id,
                                                     "updated_at": dt.datetime.now().strftime(
                                                         "%Y-%m-%d %H:%M:%S"),
                                                     "loc_assign": "true"}})
                            db2.update_one({"_id": ObjectId(location_id)},
                                           {"$set": {"employee": employee_name, "emp_id": employee_id,
                                                     "updated_at": dt.datetime.now().strftime(
                                                         "%Y-%m-%d %H:%M:%S"),
                                                     "emp_assign": "true",
                                                     "privacy_policy": "false"}})
                            response = {"status": "success",
                                        "message": f"{employee_name} assign to {location_name} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200

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


class SubAdminAssign(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                db2 = db["location"]
                data = request.get_json()
                employee_id = data["emp_id"]
                c_id = data["c_id"]
                r_id = data["r_id"]

                if employee_id and c_id and r_id:

                    employee = db1.find_one({"_id": ObjectId(employee_id), "status": "active", "type_id": "sub_admin"})

                    location = db2.find_one(
                        {"_id": ObjectId(r_id), "status": "active", "type_id": "region"})

                    if employee is None:
                        response = {"status": 'val_error', "message": {"Details": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if location is None:
                        response = {"status": 'val_error', "message": {"Details": ["Region not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        employee_name = employee.get("employee_name", None)
                        employee_assign = employee.get("assign", None)
                        employee_type = employee.get("type_id", None)
                        location_name = location.get("location", None)
                        location_assign = location.get("emp_assign", None)
                        location_type = location.get("type_id", None)

                        if employee_type != "sub_admin" or location_type != "region":
                            response = {"status": 'val_error',
                                        "message": {"Details": ["Only sub admin assign to region"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if employee_assign == "true":
                            location = employee["location"]
                            response = {"status": 'val_error', "message": {"Employee": [f"{employee_name} is already "
                                                                                        f"assign to {location}"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if location_assign == "true":
                            employee = location["employee"]
                            response = {"status": 'val_error', "message": {"Region": [f"{location_name} is already "
                                                                                      f"assign with {employee}"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        else:
                            db1.update_one({"_id": ObjectId(employee_id)},
                                           {"$set": {"location": location_name, "loc_id": r_id,
                                                     "updated_at": dt.datetime.now().strftime(
                                                         "%Y-%m-%d %H:%M:%S"),
                                                     "loc_assign": "true"}})
                            db2.update_one({"_id": ObjectId(r_id)},
                                           {"$set": {"employee": employee_name, "emp_id": employee_id,
                                                     "updated_at": dt.datetime.now().strftime(
                                                         "%Y-%m-%d %H:%M:%S"),
                                                     "emp_assign": "true"}})
                            response = {"status": "success",
                                        "message": f"{employee_name} assign to {location_name} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200

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


# class EditorAssign(MethodView):
#     @cross_origin(supports_credentials=True)
#     def post(self):
#         try:
#             start_and_check_mongo()
#             db = database_connect_mongo()
#             if db is not None:
#                 db1 = db["employee_registration"]
#                 db2 = db["location"]
#                 db3 = db["grain_assign"]
#                 data = request.get_json()
#                 employee_id = data["emp_id"]
#                 c_id = data["c_id"]
#                 r_id = data["r_id"]
#                 g_id = data["g_id"]

class PrivacyPolicyUpdate(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                data = request.get_json()
                location_id = data["loc_id"]

                if location_id:

                    location = db1.find_one({"_id": ObjectId(location_id)})

                    if location:
                        db1.update_one({"_id": ObjectId(location_id)}, {"$set": {
                            "updated_at": dt.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            "privacy_policy": "true"}})
                        response = {"status": "success",
                                    "message": f"Privacy policy updated successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Location not found"]}}
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
admin_assign = AdminAssign.as_view('admin_assign_view')
sub_admin_assign = SubAdminAssign.as_view('sub_admin_assign_view')
privacy_policy = PrivacyPolicyUpdate.as_view('privacy_policy_view')

employee_access.add_url_rule('/employee_access/registration', view_func=emp_reg, methods=['POST'])
employee_access.add_url_rule('/employee_access/all_employee', view_func=all_emp, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_details', view_func=emp_details, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_status_change', view_func=emp_status, methods=['POST'])
employee_access.add_url_rule('/employee_access/admin_assign', view_func=admin_assign, methods=['POST'])
employee_access.add_url_rule('/employee_access/sub_admin_assign', view_func=sub_admin_assign, methods=['POST'])
employee_access.add_url_rule('/employee_access/privacy_policy', view_func=privacy_policy, methods=['POST'])
