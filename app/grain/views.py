import datetime as dt
from itertools import groupby

from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError

from app.grain.grain_validation import grain_registration_schema, grain_variant_registration_schema
from app.helpers import S3Uploader
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn
from settings.configuration import S3Config

grain_add = Blueprint('grain_add', __name__)


class AddGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = dict(request.form)
                grain = data['grain']
                grain_pic = request.files.get('grain_pic')
                # print(grain_pic, "1")

                if grain and grain_pic:
                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "grain": grain, "grain_pic": grain_pic}

                    # Validate the data using the schema
                    try:
                        validated_data = grain_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        type_id = "grain"

                        # Update the created_at  field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        file_url = s3_uploader.upload_file(grain_pic, type_id=type_id, status="active")

                        if s3_uploader.check_existing_file(file_url['file_url'], type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        validated_data["grain_pic"] = file_url

                        # Add type field
                        validated_data["type_id"] = type_id

                        db1.insert_one(validated_data)

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])

                        # Create the response
                        response = {"message": "Grain added successfully", "status": "success",
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


class AddGrainVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                grain = data['grain']
                grain_variant = data['grain_variant']

                if grain and grain_variant:
                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "grain": grain, "grain_variant": grain_variant}

                    # Validate the data using the schema
                    try:
                        validated_data = grain_variant_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # Update the created_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        # Add type field
                        validated_data["type_id"] = "grain_variant"

                        db1.insert_one(validated_data)

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])

                        # Create the response
                        response = {"message": "Grain variant added successfully", "status": "success",
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


class FetchAllGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                find_grain = db1.find({"status": {"$ne": "delete"}, "type_id": "grain"},
                                      {"grain": 1, "status": 1, "grain_pic": 1}).sort("grain", 1)
                find_grain_list = list(find_grain)
                total_grain = db1.count_documents({"status": "active", "type_id": "grain"})

                if total_grain != 0:
                    for i in find_grain_list:
                        i["_id"] = str(i["_id"])
                    response = {"status": "success", "data": find_grain_list, "total_grain": total_grain,
                                "message": "Grain "
                                           "fetched "
                                           "successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200
                else:
                    response = {"status": 'val_error', "message": {"Grain": ["Please add a grain first"]}}
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


# class FetchGrain(MethodView):
#     @cross_origin(supports_credentials=True)
#     def post(self):
#         try:
#             start_and_check_mongo()
#             db = database_connect_mongo()
#             if db is not None:
#                 db1 = db["grain"]
#                 find_grain = db1.find({"status": "active"}, {"grain": 1, "_id": 0})
#                 total_grain = db1.count_documents({"status": "active", "grain": {"$exists": True}})
#
#                 if total_grain != 0:
#                     grain_list = [i["grain"] for i in find_grain]
#                     response = {"status": 'success', "data": grain_list, "total_grain": total_grain,
#                                 "message": "All country fetched successfully"}
#                     stop_and_check_mongo_status(conn)
#                     return make_response(jsonify(response)), 200
#
#                 else:
#                     response = {"status": 'val_error', "message": {"country": ["Please add a grain first"]}}
#                     stop_and_check_mongo_status(conn)
#                     return make_response(jsonify(response)), 200
#
#             else:
#                 response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
#                 stop_and_check_mongo_status(conn)
#                 return make_response(jsonify(response)), 200
#
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             response = {"status": 'val_error', "message": f'{str(e)}'}
#             stop_and_check_mongo_status(conn)
#             return make_response(jsonify(response)), 200


class FetchAllGrainVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                grain = data["grain"]

                if grain:
                    find_grain_variant = db1.find(
                        {"status": {"$ne": "delete"}, "type_id": "grain_variant", "grain": grain},
                        {"grain_variant": 1}).sort("status", 1)
                    find_grain_variant_list = list(find_grain_variant)
                    total_grain_variant = db1.count_documents(
                        {"status": "active", "type_id": "grain_variant", "grain": grain})

                    if total_grain_variant != 0:
                        for i in find_grain_variant_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": find_grain_variant_list,

                                    "total_grain_variant": total_grain_variant, "message": "Grain variant fetched "
                                                                                           "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error',
                                    "message": {"Grain_variant": ["Please add a grain variant first"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

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


class FetchAllGrainAndVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                db2 = db["content"]
                data = request.get_json()
                c_id = data["c_id"]
                r_id = data["r_id"]
                emp_assign = data["emp_assign"]

                if c_id and r_id and emp_assign:
                    find_grain_variant = db1.find(
                        {"status": "active", "c_id": c_id, "r_id": r_id,
                         "type_id": "grain_variant_assign", "emp_assign": emp_assign},
                        {"grain": 1, "grain_variant": 1, "status": 1}).sort("grain", 1)

                    find_grain_variant_list = list(find_grain_variant)
                    total_grain_variant = len(find_grain_variant_list)

                    if total_grain_variant > 0:
                        for i in find_grain_variant_list:
                            i["_id"] = str(i["_id"])

                        a = []

                        for i in find_grain_variant_list:
                            i["_id"] = str(i["_id"])
                            e = list(db2.find({"g_v_id": i["_id"]}))
                            for j in e:
                                type_id = j["type_id"]
                                status = j["status"]
                                g_v_id = j["g_v_id"]
                                a.append({"type_id": type_id, "status": status, "_id": g_v_id})
                        a.sort(key=lambda x: x['_id'])
                        result = [{'_id': k, 'approval': [{'type_id': x['type_id'], 'status': x['status']} for x in v]}
                                  for
                                  k, v in groupby(a, key=lambda x: x['_id'])]

                        # Create a dictionary to map _id values to documents in list1
                        id_map = {doc['_id']: doc for doc in find_grain_variant_list}

                        # Iterate over list2 and append approval field to corresponding document in list1
                        for doc in result:
                            if doc['_id'] in id_map:
                                id_map[doc['_id']]['approval'] = doc['approval']

                        # Convert the dictionary back to a list
                        result = list(id_map.values())

                        response = {"status": "success", "data": result,
                                    "total_grain_variant": total_grain_variant, "message": "Data "
                                                                                           "fetched "
                                                                                           "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error', "message": {"Grain_variant": ["Please add a grain variant "
                                                                                         "first"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

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


class FetchGDetails(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                g_id = data["g_id"]
                type_id = data["type_id"]

                if g_id and type_id:
                    find_details = db1.find_one(
                        {"_id": ObjectId(g_id), "status": {"$ne": "delete"}, "type_id": type_id})

                    if find_details:
                        find_details["_id"] = str(find_details["_id"])
                        response = {"status": "success", "data": find_details, "message": "Grain details fetched "
                                                                                          "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Grain not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


class GStatusChange(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                g_status = data["g_status"].lower()
                gs_id = data["gs_id"]
                type_id = data["type_id"]

                if g_status and gs_id and type_id:

                    current_status = db1.find_one({"_id": ObjectId(gs_id), "type_id": type_id, }, {"status": 1})

                    if current_status is None:
                        response = {"status": 'val_error', "message": {"DB": ["Data not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == "delete":
                        response = {"status": 'val_error', "message": {"Details": ["Grain not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == g_status:
                        response = {"status": 'val_error', "message": {"Details": [f"Grain is already {g_status}"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        update_status = db1.update_one(
                            {"_id": ObjectId(gs_id), "type_id": type_id, "status": {"$ne": "delete"}},
                            {"$set": {"status": g_status,
                                      "updated_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}})

                        if update_status.acknowledged and update_status.modified_count == 1:
                            response = {"status": "success", "message": f"Grain {g_status} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": "error", "message": "Grain not updated"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
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


class GAStatusChange(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                data = request.get_json()
                g_status = data["g_status"].lower()
                gs_id = data["gs_id"]
                type_id = data["type_id"]

                if g_status and gs_id and type_id:

                    current_status = db1.find_one({"_id": ObjectId(gs_id), "type_id": type_id, }, {"status": 1})

                    if current_status is None:
                        response = {"status": 'val_error', "message": {"DB": ["Data not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == "delete":
                        response = {"status": 'val_error', "message": {"Details": ["Grain not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == g_status:
                        response = {"status": 'val_error', "message": {"Details": [f"Grain is already {g_status}"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        update_status = db1.update_one(
                            {"_id": ObjectId(gs_id), "type_id": type_id, "status": {"$ne": "delete"}},
                            {"$set": {"status": g_status,
                                      "updated_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}})

                        if update_status.acknowledged and update_status.modified_count == 1:
                            response = {"status": "success", "message": f"Grain {g_status} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": "error", "message": "Grain not updated"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
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


class AssignGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                db2 = db["location"]
                db3 = db["grain_assign"]
                data = request.get_json()
                g_id = data["g_id"]
                loc_id = data["loc_id"]

                if g_id and loc_id:

                    find_grain = db1.find_one({"_id": ObjectId(g_id), "status": "active"})
                    grain_name = find_grain["grain"]
                    grain_pic = find_grain["grain_pic"]

                    find_location = db2.find_one({"_id": ObjectId(loc_id), "status": "active"})
                    location_name = find_location["location"]

                    if find_grain and find_location:

                        grain_assign = db3.find_one(
                            {"grain": grain_name, "country": location_name, "status": {"$ne": "delete"}})

                        if grain_assign is not None:

                            response = {"status": 'val_error', "message": {"Details": ["Grain already assigned"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        else:

                            db3.insert_one({"grain": grain_name, "country": location_name, "status": "active",
                                            "grain_pic": grain_pic,
                                            "type_id": "grain_assign", "g_id": g_id, "loc_id": loc_id,
                                            "created_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                            "updated_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})

                            response = {"status": "success",
                                        "message": f"{grain_name} assigned to {location_name} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Grain or location not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

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


class FetchSpecificGrain(MethodView):

    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                data = request.get_json()
                c_id = data["c_id"]

                if c_id:
                    find_grain = db1.find({"loc_id": c_id, "status": "active", "type_id": "grain_assign"},
                                          {"grain": 1, "status": 1}).sort("grain", 1)
                    grain_list = list(find_grain)
                    total_grain = len(grain_list)

                    if total_grain > 0:

                        for i in grain_list:
                            i["_id"] = str(i["_id"])

                        response = {"status": "success", "data": grain_list,
                                    "total_grain": total_grain, "message": "Grains "
                                                                           "fetched "
                                                                           "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Grain not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

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


# class FetchSpecificGrainVariant1(MethodView):
#     @cross_origin(supports_credentials=True)
#     def post(self):
#         try:
#             start_and_check_mongo()
#             db = database_connect_mongo()
#             if db is not None:
#                 db1 = db["grain_assign"]
#                 data = request.get_json()
#                 c_id = data["c_id"]
#                 r_id = data["r_id"]
#                 g_a_id = data["g_a_id"]
#                 emp_assign = data["emp_assign"]
#
#                 if c_id and r_id and g_a_id and emp_assign:
#                     find_grain_variant = db1.find(
#                         {"status": "active", "c_id": c_id, "r_id": r_id, "g_a_id": g_a_id,
#                          "type_id": "grain_variant_assign", "emp_assign": emp_assign},
#                         {"grain_variant": 1, "status": 1}).sort("grain_variant", 1)
#                     find_grain_variant_list = list(find_grain_variant)
#                     total_grain_variant = len(find_grain_variant_list)
#
#                     if total_grain_variant > 0:
#                         for i in find_grain_variant_list:
#                             i["_id"] = str(i["_id"])
#                         response = {"status": "success", "data": find_grain_variant_list,
#                                     "total_grain_variant": total_grain_variant, "message": "Grain variant "
#                                                                                            "fetched "
#                                                                                            "successfully"}
#                         stop_and_check_mongo_status(conn)
#                         return make_response(jsonify(response)), 200
#
#                 elif c_id and r_id and g_a_id and not emp_assign:
#                     find_grain_variant = db1.find(
#                         {"status": "active", "c_id": c_id, "r_id": r_id, "g_a_id": g_a_id,
#                          "type_id": "grain_variant_assign"},
#                         {"grain_variant": 1, "status": 1}).sort("grain_variant", 1)
#                     find_grain_variant_list = list(find_grain_variant)
#                     total_grain_variant = len(find_grain_variant_list)
#
#                     if total_grain_variant > 0:
#                         for i in find_grain_variant_list:
#                             i["_id"] = str(i["_id"])
#                         response = {"status": "success", "data": find_grain_variant_list,
#                                     "total_grain_variant": total_grain_variant, "message": "Grain variant "
#                                                                                            "fetched "
#                                                                                            "successfully"}
#                         stop_and_check_mongo_status(conn)
#                         return make_response(jsonify(response)), 200
#
#                     else:
#                         response = {"status": 'val_error', "message": {"Grain_variant": ["Please add a grain variant "
#                                                                                          "first"]}}
#                         stop_and_check_mongo_status(conn)
#                         return make_response(jsonify(response)), 400
#
#                 else:
#                     response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
#                     stop_and_check_mongo_status(conn)
#                     return make_response(jsonify(response)), 400
#
#             else:
#                 response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
#                 stop_and_check_mongo_status(conn)
#                 return make_response(jsonify(response)), 400
#
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             response = {"status": 'val_error', "message": f'{str(e)}'}
#             stop_and_check_mongo_status(conn)
#             return make_response(jsonify(response)), 400


# class FetchSpecificGrainVariant(MethodView):
#     @cross_origin(supports_credentials=True)
#     def post(self):
#         try:
#             start_and_check_mongo()
#             db = database_connect_mongo()
#             if db is None:
#                 return make_response(jsonify({
#                     "status": 'val_error',
#                     "message": {"Details": ["Database connection failed"]}
#                 })), 400
#
#             db1 = db["grain_assign"]
#             data = request.get_json()
#
#             # Input validation
#             required_fields = ['c_id', 'r_id', 'g_a_id', 'emp_assign']
#
#             # if not all(field in data for field in required_fields):
#             #     return make_response(jsonify({
#             #         "status": 'val_error',
#             #         "message": {"Details": ["Missing required fields"]}
#             #     })), 400
#
#             # missing_fields = [field for field in required_fields if field not in data]
#             # if missing_fields:
#             #     return make_response(jsonify({
#             #         "status": 'val_error',
#             #         "message": {
#             #             "Details": ["Missing required fields"],
#             #             "missing_fields": missing_fields
#             #         }
#             #     })), 400
#
#             missing_fields = [field for field in required_fields if field not in data]
#             if missing_fields:
#                 return make_response(jsonify({
#                     "status": 'val_error',
#                     "message": {"Details": [f"Missing required fields: {', '.join(missing_fields)}"]}
#                 })), 400
#
#             c_id = data["c_id"]
#             r_id = data["r_id"]
#             g_a_id = data["g_a_id"]
#             emp_assign = data["emp_assign"]
#
#             # Base query
#             query = {
#                 "status": "active",
#                 "c_id": c_id,
#                 "r_id": r_id,
#                 "g_a_id": g_a_id,
#                 "type_id": "grain_variant_assign"
#             }
#
#             # Add emp_assign to query if it exists
#             if emp_assign:
#                 query["emp_assign"] = emp_assign
#
#             find_grain_variant = db1.find(
#                 query,
#                 {"grain_variant": 1, "status": 1}
#             ).sort("grain_variant", 1)
#
#             find_grain_variant_list = list(find_grain_variant)
#             total_grain_variant = len(find_grain_variant_list)
#
#             if total_grain_variant == 0:
#                 return make_response(jsonify({
#                     "status": 'val_error',
#                     "message": {"Grain_variant": ["Please add a grain variant first"]}
#                 })), 400
#
#             # Convert ObjectId to string
#             for variant in find_grain_variant_list:
#                 variant["_id"] = str(variant["_id"])
#
#             response = {
#                 "status": "success",
#                 "data": find_grain_variant_list,
#                 "total_grain_variant": total_grain_variant,
#                 "message": "Grain variant fetched successfully"
#             }
#
#             return make_response(jsonify(response)), 200
#
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             return make_response(jsonify({
#                 "status": 'val_error',
#                 "message": str(e)
#             })), 500
#
#         finally:
#             if conn:
#                 stop_and_check_mongo_status(conn)


class FetchSpecificGrainVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is None:
                return make_response(jsonify({
                    "status": 'val_error',
                    "message": {"Details": ["Database connection failed"]}
                })), 400

            db1 = db["grain_assign"]
            data = request.get_json()

            # Input validation
            required_fields = ['c_id', 'r_id', 'g_a_id', 'emp_assign']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return make_response(jsonify({
                    "status": 'val_error',
                    "message": {"Details": [f"Missing required fields: {', '.join(missing_fields)}"]}
                })), 400

            # #Normal approach
            # c_id = data["c_id"]
            # r_id = data["r_id"]
            # g_a_id = data["g_a_id"]
            # emp_assign = data["emp_assign"]

            # Option 1: Multiple assignments in one line
            # c_id, r_id, g_a_id, emp_assign = data["c_id"], data["r_id"], data["g_a_id"], data["emp_assign"]

            # Option 2: List comprehension
            c_id, r_id, g_a_id, emp_assign = [data[key] for key in ("c_id", "r_id", "g_a_id", "emp_assign")]

            # Option 3: Using operator.itemgetter (if you want to import it)
            # from operator import itemgetter
            # c_id, r_id, g_a_id, emp_assign = itemgetter("c_id", "r_id", "g_a_id", "emp_assign")(data)

            # Base query
            if not emp_assign:  # If emp_assign has no value

                query = {
                    "status": "active",
                    "c_id": c_id,
                    "r_id": r_id,
                    "g_a_id": g_a_id,
                    "type_id": "grain_variant_assign"
                }

            else:  # If emp_assign has a value
                query = {
                    "status": "active",
                    "c_id": c_id,
                    "r_id": r_id,
                    "g_a_id": g_a_id,
                    "type_id": "grain_variant_assign",
                    "emp_assign": emp_assign
                }

            find_grain_variant = db1.find(
                query,
                {"grain_variant": 1, "status": 1}
            ).sort("grain_variant", 1)

            if not find_grain_variant:
                return make_response(jsonify({
                    "status": 'val_error',
                    "message": {"Grain_variant": ["Please add a grain variant first"]}
                })), 400

            find_grain_variant_list = list(find_grain_variant)
            total_grain_variant = len(find_grain_variant_list)

            # Convert ObjectId to string
            for variant in find_grain_variant_list:
                variant["_id"] = str(variant["_id"])

            response = {
                "status": "success",
                "data": find_grain_variant_list,
                "total_grain_variant": total_grain_variant,
                "message": "Grain variant fetched successfully"
            }

            return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return make_response(jsonify({
                "status": 'val_error',
                "message": str(e)
            })), 500

        finally:
            stop_and_check_mongo_status(conn)


class AssignGrainVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["location"]
                db3 = db["grain_assign"]
                data = dict(request.form)
                c_id = data["c_id"]
                r_id = data["r_id"]
                g_a_id = data["g_a_id"]
                grain_variant = data["grain_variant"]
                gv_pic = request.files.get("gv_pic", None)
                #
                # if gv_pic and c_id and r_id and g_a_id and grain_variant:
                #     print(gv_pic)
                #
                # else:
                #     print("else")

                if c_id and r_id and g_a_id and grain_variant and gv_pic:

                    find_country = db1.find_one({"_id": ObjectId(c_id), "status": "active", "type_id": "country"})
                    if not find_country:
                        response = {"message": {"Details": ["Country not found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    country_name = find_country.get("location", "None")

                    find_region = db1.find_one({"_id": ObjectId(r_id), "status": "active", "type_id": "region"})
                    if not find_region:
                        response = {"message": {"Details": ["Region not found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    region_name = find_region.get("location", "None")

                    find_grain = db3.find_one({"_id": ObjectId(g_a_id), "status": "active", "type_id": "grain_assign"})
                    if not find_grain:
                        response = {"message": {"Details": ["Grain not found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    grain_name = find_grain.get("grain", "None")

                    validates_fields = {"grain": grain_name, "grain_variant": grain_variant, "gv_pic": gv_pic,
                                        "status": "active",
                                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "updated_at": None}

                    try:
                        validate_data = grain_variant_registration_schema.load(validates_fields)

                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if find_country and find_region and find_grain:

                        grain_variant_assign = db3.find_one(
                            {"grain": grain_name, "country": country_name, "region": region_name,
                             "grain_variant": grain_variant, "status": {"$ne": "delete"}})

                        if grain_variant_assign:

                            response = {"status": 'val_error',
                                        "message": {"Details": ["Grain variant already assigned"]}}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        else:
                            type_id = "grain_variant_assign"

                            # if gv_pic and not allowed_file(gv_pic.filename):
                            #     response = {"message": {"File": ["File type not allowed"]}, "status": "val_error"}
                            #     stop_and_check_mongo_status(conn)
                            #     return make_response(jsonify(response)), 400

                            s3_config = S3Config()
                            bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                            s3_uploader = S3Uploader(s3_config)
                            file_url = s3_uploader.upload_file(gv_pic, type_id=type_id, status="active")

                            if s3_uploader.check_existing_file(file_url['file_url'], type_id):
                                response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                                stop_and_check_mongo_status(conn)
                                return make_response(jsonify(response)), 400

                            validate_data["type_id"] = type_id
                            validate_data["approve_status"] = "pending"
                            validate_data["emp_assign"] = "false"
                            validate_data["country"] = country_name
                            validate_data["region"] = region_name
                            validate_data["c_id"] = c_id
                            validate_data["r_id"] = r_id
                            validate_data["g_a_id"] = g_a_id
                            validate_data["gv_pic"] = file_url
                            validate_data["created_at"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            validate_data["updated_at"] = None

                            db3.insert_one(validate_data)

                            # db3.insert_one({"grain": grain_name, "country": country_name, "region": region_name,
                            #                 "grain_variant": grain_variant, "status": "active",
                            #                 "approve_status": "pending", "emp_assign": "false",
                            #                 "type_id": "grain_variant_assign", "c_id": c_id, "r_id": r_id,
                            #                 "g_a_id": g_a_id,
                            #                 "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            #                 "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

                            response = {"status": "success",
                                        "message": f"{grain_variant} assigned to {region_name} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200

                    else:
                        response = {"status": 'val_error', "message": {"Details": ["Grain or location not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                else:
                    response = {"status": 'val_error', "message": {"Details": ["All fields are required"]}}
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


class GrainVariantStatusChange(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                data = request.get_json()
                g_a_status = data["g_a_status"].lower()
                g_a_id = data["g_a_id"]

                if g_a_status and g_a_id:

                    current_status = db1.find_one({"_id": ObjectId(g_a_id), "status": {"$ne": "delete"}})

                    if current_status is None:
                        response = {"status": 'val_error', "message": {"DB": ["Data not found"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if current_status["status"] == g_a_status:
                        response = {"status": 'val_error',
                                    "message": {"Details": [f"Grain variant is already {g_a_status}"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        update_status = db1.update_one(
                            {"_id": ObjectId(g_a_id), "status": {"$ne": "delete"}},
                            {"$set": {"status": g_a_status,
                                      "updated_at": str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}})

                        if update_status.acknowledged and update_status.modified_count == 1:
                            response = {"status": "success", "message": f"Grain variant {g_a_status} successfully"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 200
                        else:
                            response = {"status": "val_error", "message": "Grain variant not updated"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
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


class FetchAllGrainVariantBaseOnRegion(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                data = request.get_json()
                r_id = data["r_id"]
                emp_assign = data["emp_assign"]

                if r_id and emp_assign:
                    find_all_grain_variant = db1.find(
                        {"r_id": r_id, "status": "active", "type_id": "grain_variant_assign",
                         "emp_assign": emp_assign}).sort(
                        "grain_variant", 1)
                    grain_variant_list = list(find_all_grain_variant)
                    total_grain_variant = len(grain_variant_list)
                    if total_grain_variant != 0:
                        for i in grain_variant_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": grain_variant_list,
                                    "total_grain_variant": total_grain_variant,
                                    "message": "Employee "
                                               "fetched "
                                               "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": "val_error", "message": "No grain variant found"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 404

                elif r_id and not emp_assign:
                    find_all_grain_variant = db1.find(
                        {"r_id": r_id, "status": "active", "type_id": "grain_variant_assign"}).sort(
                        "grain_variant", 1)
                    grain_variant_list = list(find_all_grain_variant)
                    total_grain_variant = len(grain_variant_list)
                    if total_grain_variant != 0:
                        for i in grain_variant_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": grain_variant_list,
                                    "total_grain_variant": total_grain_variant,
                                    "message": "Employee "
                                               "fetched "
                                               "successfully"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"status": "val_error", "message": "No grain variant found"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 404

                else:
                    response = {"status": 'val_error', "message": {"Details": ["Please enter correct details"]}}
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


grain_add_view = AddGrain.as_view('grain_add_view')
grain_variant_add_view = AddGrain.as_view('grain_variant_add_view')
grain_fetch_view = FetchAllGrain.as_view('grain_fetch_view')
grain_variant_fetch_view = FetchAllGrainVariant.as_view('grain_fetch_variant_view')
g_status_change = GStatusChange.as_view('g_status')
grain_assign_status_change = GAStatusChange.as_view('grain_assign_status_change')
g_details = FetchGDetails.as_view('g_details')
assign_grain = AssignGrain.as_view('grain_assign')
assign_grain_variant = AssignGrainVariant.as_view('grain_assign_variant')
specific_grain_variant_fetch = FetchSpecificGrainVariant.as_view('specific_grain_variant_fetch')
grain_variant_status_change = GrainVariantStatusChange.as_view('grain_variant_status_change')
specific_grain_fetch = FetchSpecificGrain.as_view('specific_grain_fetch')
fetch_all_grain_and_variant = FetchAllGrainAndVariant.as_view('fetch_all_grain_variant')
fetch_all_grain_variant_base_on_region = FetchAllGrainVariantBaseOnRegion.as_view(
    'fetch_all_grain_variant_base_on_region')

grain_add.add_url_rule('/grain/add_grain', view_func=grain_add_view, methods=['POST'])
grain_add.add_url_rule('/grain/add_grain_variant', view_func=grain_variant_add_view, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_grain', view_func=grain_fetch_view, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_grain_variant', view_func=grain_variant_fetch_view, methods=['POST'])
grain_add.add_url_rule('/grain/g_status_change', view_func=g_status_change, methods=['POST'])
grain_add.add_url_rule('/grain/g_a_status_change', view_func=grain_assign_status_change, methods=['POST'])
grain_add.add_url_rule('/grain/g_details', view_func=g_details, methods=['POST'])
grain_add.add_url_rule('/grain/assign_grain', view_func=assign_grain, methods=['POST'])
grain_add.add_url_rule('/grain/assign_grain_variant', view_func=assign_grain_variant, methods=['POST'])
grain_add.add_url_rule('/grain/specific_grain_variant_fetch', view_func=specific_grain_variant_fetch, methods=['POST'])
grain_add.add_url_rule('/grain/grain_variant_status_change', view_func=grain_variant_status_change, methods=['POST'])
grain_add.add_url_rule('/grain/specific_grain_fetch', view_func=specific_grain_fetch, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_all_grain_and_variant', view_func=fetch_all_grain_and_variant, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_all_grain_variant_base_on_region',
                       view_func=fetch_all_grain_variant_base_on_region, methods=['POST'])
