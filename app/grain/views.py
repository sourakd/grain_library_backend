import datetime as dt

from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError

from app.grain.grain_validation import grain_registration_schema, grain_variant_registration_schema
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn

grain_add = Blueprint('grain_add', __name__)


class AddGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                grain = data['grain'].lower()

                if grain:
                    # Validate the data using the schema
                    data = {"status": "active",
                            "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                            "grain": grain}

                    # Validate the data using the schema
                    try:
                        validated_data = grain_registration_schema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        # Add type field
                        validated_data["type_id"] = "grain"

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
                response = {"status": 'val_error', "message": "Database connection failed"}
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
                    grain = data['grain'].lower()
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
                            # Update the updated_at field
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
                    response = {"status": 'val_error', "message": "Database connection failed"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

            except Exception as e:
                import traceback
                traceback.print_exc()
                response = {"status": 'val_error', "message": f'{str(e)}'}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400


class FetchGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                find_grain = db1.find({"status": "active", "type_id": "grain"}, {"grain": 1})
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
#                 response = {"status": 'val_error', "message": "Database connection failed"}
#                 stop_and_check_mongo_status(conn)
#                 return make_response(jsonify(response)), 200
#
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             response = {"status": 'val_error', "message": f'{str(e)}'}
#             stop_and_check_mongo_status(conn)
#             return make_response(jsonify(response)), 200


class FetchGrainVariant(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain"]
                data = request.get_json()
                grain = data["grain"].lower()

                if grain:
                    find_grain_variant = db1.find({"status": "active", "type_id": "grain_variant", "grain": grain},
                                                  {"grain_variant": 1})
                    find_grain_variant_list = list(find_grain_variant)
                    total_grain_variant = db1.count_documents(
                        {"status": "active", "type_id": "grain_variant", "grain": grain})

                    if total_grain_variant != 0:
                        for i in find_grain_variant_list:
                            i["_id"] = str(i["_id"])
                        response = {"status": "success", "data": find_grain_variant_list,
                                    "total_grain_variant": total_grain_variant, "message": "Grain variant "
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
                response = {"status": 'val_error', "message": "Database connection failed"}
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
                        {"_id": ObjectId(g_id), "status": {"$in": ["active", "inactive"]}, "type_id": type_id})

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
                    current_status = db1.find_one({"_id": ObjectId(gs_id), "type_id": type_id}, {"status": 1})
                    if current_status["status"] == g_status:
                        response = {"status": 'val_error', "message": {"Details": [f"Grain is already {g_status}"]}}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        db1.update_one({"_id": ObjectId(gs_id), "type_id": type_id}, {"$set": {"status": g_status}})
                        response = {"status": "success", "message": f"Grain {g_status} successfully"}
                        stop_and_check_mongo_status(conn)
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


grain_add_view = AddGrain.as_view('grain_add_view')
grain_variant_add_view = AddGrain.AddGrainVariant.as_view('grain_variant_add_view')
grain_fetch_view = FetchGrain.as_view('grain_fetch_view')
grain_variant_fetch_view = FetchGrainVariant.as_view('grain_fetch_variant_view')
g_status = GStatusChange.as_view('g_status')
g_details = FetchGDetails.as_view('g_details')

grain_add.add_url_rule('/grain/add_grain', view_func=grain_add_view, methods=['POST'])
grain_add.add_url_rule('/grain/add_grain_variant', view_func=grain_variant_add_view, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_grain', view_func=grain_fetch_view, methods=['POST'])
grain_add.add_url_rule('/grain/fetch_grain_variant', view_func=grain_variant_fetch_view, methods=['POST'])
grain_add.add_url_rule('/grain/g_status', view_func=g_status, methods=['POST'])
grain_add.add_url_rule('/grain/g_details', view_func=g_details, methods=['POST'])
