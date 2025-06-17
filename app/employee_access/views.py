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
                employee_name = data["employee_name"]
                email_id = data["email_id"].lower()
                type_id = data["type_id"].lower()
                address = data["address"]
                id_proof = data["id_proof"].lower()
                phone_number = data["phone_number"]
                id_no = data["id_no"]
                profile_pic = request.files.get("profile_pic")

                if employee_name and email_id and phone_number and type_id and profile_pic and address and id_proof and id_no:

                    status = "active"
                    # emp_schema = EmployeeRegistrationSchema()

                    data = {"status": status, "type_id": type_id,
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
                        # Update the created_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        file_url = s3_uploader.upload_file(profile_pic, type_id=type_id, status="active")

                        if s3_uploader.check_existing_file(file_url['file_url'], type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
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
                                    "message": "Employee fetched successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": 'val_error', "message": {"Employee": ["Please add an employee first"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                if type_id and assign:
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
                                    "message": "Employee fetched successfully"}
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


class EmployeeBasedOnLocation(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                db2 = db["location"]
                data = request.get_json()
                country = data["c_id"]
                region = data["r_id"]
                type_id = data["type_id"]

                if country and type_id and region is None or region == "":
                    if type_id == "admin":
                        find_employee = db1.find_one(
                            {"status": {"$ne": "delete"}, "type_id": type_id, "loc_id": country, "loc_assign": "true"},
                            {"password": 0})
                        total_employee = db1.count_documents(
                            {"status": {"$ne": "delete"}, "type_id": type_id, "loc_id": country, "loc_assign": "true"})
                        if total_employee != 0:
                            find_employee["_id"] = str(find_employee["_id"])
                            response = {"status": "success", "data": find_employee,
                                        "total_employee": total_employee,
                                        "message": "Employee fetched successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": 'val_error',
                                        "message": {"Employee": ["Please add an employee first 1"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                    if type_id == "region":
                        employee_list = []
                        find_employee = db2.find(
                            {"status": {"$ne": "delete"}, "type_id": type_id, "c_id": country, "emp_assign": "true"},
                            {"emp_id": 1})
                        find_employee_list = list(find_employee)
                        total_employee = db2.count_documents(
                            {"status": {"$ne": "delete"}, "type_id": type_id, "c_id": country})
                        if total_employee != 0:
                            for i in find_employee_list:
                                emp_id = i["emp_id"]
                                find_employee = db1.find_one(
                                    {"status": {"$ne": "delete"}, "type_id": "sub_admin", "_id": ObjectId(emp_id)},
                                    {"password": 0})
                                find_employee["_id"] = str(find_employee["_id"])
                                employee_list.append(find_employee)

                            response = {"status": "success", "data": employee_list,
                                        "total_employee": total_employee,
                                        "message": "Employee "
                                                   "fetched "
                                                   "successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": 'val_error',
                                        "message": {"Employee": ["Please add an employee first 2"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Please enter type ID"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                if region and type_id and country is None or country == "":
                    find_employee = db1.find(
                        {"status": {"$ne": "delete"}, "type_id": type_id, "loc_id": region, "loc_assign": "true"},
                        {"password": 0}).sort("employee_name", 1)
                    find_employee_list = list(find_employee)
                    total_employee = db1.count_documents(
                        {"status": {"$ne": "delete"}, "type_id": type_id, "loc_id": region, "loc_assign": "true"})
                    if total_employee != 0:
                        for i in find_employee_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": find_employee_list,
                                    "total_employee": total_employee,
                                    "message": "Employee "
                                               "fetched "
                                               "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": 'val_error', "message": {"Employee": ["Please add an employee first 3"]}}
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


class EmployeeDetails(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                db2 = db["location"]
                db3 = db["grain_assign"]
                data = request.get_json()
                type_id = data["type_id"]
                employee_id = data["emp_id"]

                if type_id and employee_id:

                    find_employee = db1.find_one(
                        {"status": {"$ne": "delete"}, "type_id": type_id, "_id": ObjectId(employee_id)},
                        {"password": 0})

                    if not find_employee:
                        response = {"status": 'val_error', "message": {"Employee": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if type_id == "editor":

                        loc_id = find_employee["loc_id"]
                        if not loc_id:
                            response = {"status": 'val_error', "message": {"Employee": ["Employee type not found"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        g_v_id = find_employee["g_v_id"]
                        if not g_v_id:
                            response = {"status": 'val_error', "message": {"Employee": ["Employee type not found"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if find_employee:

                            find_location = db2.find_one(
                                {"status": {"$ne": "delete"}, "_id": ObjectId(loc_id), "emp_assign": "true"},
                                {"location": 1, "employee": 1})

                            location = find_location.get("location", "location not found")
                            employee = find_location.get("employee", "Employee not found")

                            find_grain_variant = db3.find_one(
                                {"status": {"$ne": "delete"}, "_id": ObjectId(g_v_id)},
                                {"grain_variant": 1})

                            grain_variant = find_grain_variant.get("grain_variant", "Grain variant not found")

                            find_employee["_id"] = str(find_employee["_id"])
                            find_employee["location"] = location
                            find_employee["employee"] = employee
                            find_employee["grain_variant"] = grain_variant
                            response = {"status": "success", "data": find_employee,
                                        "message": "Employee fetched successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": 'val_error', "message": {"Employee": ["Employee not found"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                    if type_id != "editor":
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
                                      "updated_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}})

                        if update_status.acknowledged and update_status.modified_count == 1:
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
                        employee_assign = employee.get("loc_assign", None)
                        employee_type = employee.get("type_id", None)
                        location_name = location.get("location", None)
                        location_assign = location.get("emp_assign", None)
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
                            update_status_employee = db1.update_one({"_id": ObjectId(employee_id)},
                                                                    {"$set": {"location": location_name,
                                                                              "loc_id": location_id,
                                                                              "updated_at": str(
                                                                                  dt.datetime.now().strftime(
                                                                                      "%Y-%m-%d %H:%M:%S")),
                                                                              "loc_assign": "true"}})

                            update_status_location = db2.update_one({"_id": ObjectId(location_id)},
                                                                    {"$set": {"employee": employee_name,
                                                                              "emp_id": employee_id,
                                                                              "updated_at": str(
                                                                                  dt.datetime.now().strftime(
                                                                                      "%Y-%m-%d %H:%M:%S")),
                                                                              "emp_assign": "true",
                                                                              "privacy_policy": "false"}})

                            if update_status_employee.acknowledged and update_status_employee.modified_count == 1 and \
                                    update_status_location.acknowledged and update_status_location.modified_count == 1:
                                response = {"status": "success",
                                            "message": f"{employee_name} assign to {location_name} successfully"}
                                stop_and_check_mongo_status(conn)
                                return make_response(jsonify(response)), 200

                            else:
                                response = {"status": "val_error",
                                            "message": {"details": ["Failed to assign employee to location"]}}
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
                        employee_assign = employee.get("loc_assign", None)
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
                            update_status_employee = db1.update_one({"_id": ObjectId(employee_id)},
                                                                    {"$set": {"location": location_name, "loc_id": r_id,
                                                                              "updated_at": str(
                                                                                  dt.datetime.now().strftime(
                                                                                      "%Y-%m-%d %H:%M:%S")),
                                                                              "loc_assign": "true"}})

                            update_status_location = db2.update_one({"_id": ObjectId(r_id)},
                                                                    {"$set": {"employee": employee_name,
                                                                              "emp_id": employee_id,
                                                                              "updated_at": str(
                                                                                  dt.datetime.now().strftime(
                                                                                      "%Y-%m-%d %H:%M:%S")),
                                                                              "emp_assign": "true"}})

                            if update_status_employee.acknowledged and update_status_employee.modified_count == 1 and \
                                    update_status_location.acknowledged and update_status_location.modified_count == 1:
                                response = {"status": "success",
                                            "message": f"{employee_name} assign to {location_name} successfully"}
                                stop_and_check_mongo_status(conn)
                                return make_response(jsonify(response)), 200

                            else:
                                response = {"status": "val_error",
                                            "message": {"details": ["Failed to assign employee to location"]}}
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


class EditorAssign(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["employee_registration"]
                db2 = db["location"]
                db3 = db["grain_assign"]
                data = request.get_json()
                employee_id = data["emp_id"]
                g_v_id = data["g_v_id"]
                r_id = data["r_id"]

                if employee_id and g_v_id and r_id:

                    editor = db1.find_one({"_id": ObjectId(employee_id), "status": "active", "type_id": "editor"})
                    grain_variant = db3.find_one(
                        {"_id": ObjectId(g_v_id), "status": "active", "type_id": "grain_variant_assign"})
                    location = db2.find_one({"_id": ObjectId(r_id), "status": "active", "type_id": "region"})

                    if editor["loc_assign"] == "true":
                        response = {"status": 'val_error', "message": {"Employee": ["Editor is already assign"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if grain_variant["emp_assign"] == "true":
                        response = {"status": 'val_error',
                                    "message": {"Grain variant": ["Grain variant is already assign"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if not editor:
                        response = {"status": 'val_error', "message": {"Details": ["Employee not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if not grain_variant:
                        response = {"status": 'val_error', "message": {"Details": ["Grain variant not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if not location:
                        response = {"status": 'val_error', "message": {"Details": ["Region not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        editor_update = db1.update_one({"_id": ObjectId(employee_id)}, {"$set": {
                            "updated_at": str(dt.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")),
                            "loc_id": r_id, "loc_assign": "true", "g_v_id": g_v_id}})

                        grain_variant_update = db3.update_one({"_id": ObjectId(g_v_id)}, {"$set": {
                            "updated_at": str(dt.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")),
                            "editor_id": employee_id, "emp_assign": "true", "employee": editor["employee_name"]}})

                        if editor_update.acknowledged and editor_update.modified_count == 1 and \
                                grain_variant_update.acknowledged and grain_variant_update.modified_count == 1:
                            response = {"status": "success",
                                        "message": "Editor assign to region and grain variant successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": "val_error",
                                        "message": "Failed to assign editor to region and grain variant"}
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
                        pp_status = location.get("privacy_policy", None)

                        if pp_status == "true":
                            response = {"status": 'val_error',
                                        "message": {"Details": ["Privacy policy already accepted"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        else:
                            privacy_policy_update = db1.update_one({"_id": ObjectId(location_id)}, {"$set": {
                                "updated_at": str(dt.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")),
                                "privacy_policy": "true"}})

                            if privacy_policy_update.acknowledged and privacy_policy_update.modified_count == 1:
                                response = {"status": "success",
                                            "message": "Privacy policy updated successfully"}
                                stop_and_check_mongo_status(conn)
                                return make_response(jsonify(response)), 200

                            else:
                                response = {"status": 'val_error',
                                            "message": {"Details": ["Privacy policy not update"]}}
                                stop_and_check_mongo_status(conn)
                                return make_response(jsonify(response)), 400

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
emp_details_loc = EmployeeBasedOnLocation.as_view('emp_details_loc_view')
editor_assign = EditorAssign.as_view('editor_assign_view')

employee_access.add_url_rule('/employee_access/registration', view_func=emp_reg, methods=['POST'])
employee_access.add_url_rule('/employee_access/all_employee', view_func=all_emp, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_details', view_func=emp_details, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_status_change', view_func=emp_status, methods=['POST'])
employee_access.add_url_rule('/employee_access/admin_assign', view_func=admin_assign, methods=['POST'])
employee_access.add_url_rule('/employee_access/sub_admin_assign', view_func=sub_admin_assign, methods=['POST'])
employee_access.add_url_rule('/employee_access/privacy_policy', view_func=privacy_policy, methods=['POST'])
employee_access.add_url_rule('/employee_access/employee_details_location', view_func=emp_details_loc, methods=['POST'])
employee_access.add_url_rule('/employee_access/editor_assign', view_func=editor_assign, methods=['POST'])
