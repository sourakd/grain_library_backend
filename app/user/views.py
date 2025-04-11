from flask import make_response, jsonify, Blueprint, request
from flask.views import MethodView
from flask_cors import cross_origin

from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn

user = Blueprint('user', __name__)


class FetchGrain(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["grain_assign"]
                find_grain = db1.find({"status": "active", "type_id": "grain_variant_assign"},
                                      {"grain": 1})
                find_grain_list = list(find_grain)

                if find_grain_list is not None:

                    unique_grains = {}

                    for item in find_grain_list:
                        unique_grains[item["grain"]] = item
                        unique_grains[item["grain"]]["_id"] = str(item["_id"])

                    unique_grain_list = list(unique_grains.values())

                    total_grain = len(unique_grain_list)

                    response = {"status": 'success', "data": unique_grain_list, "total_grain": total_grain,
                                "message": "All grain fetched successfully"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 200

                else:
                    response = {"status": 'val_error', "message": {"country": ["Please assign a grain variant first"]}}
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
            return make_response(jsonify(response)), 500


class FetchCountryBasedOnGrain(MethodView):
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
            required_fields = ["grain"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                response = {"status": 'val_error',
                            "message": {"Details": [f"{field} is required"] for field in missing_fields}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

            grain = data["grain"]

            if not grain:

                response = {"status": 'val_error', "message": {"grain": ["Please select a grain"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

            else:

                query = {"status": "active", "type_id": "grain_assign", "grain": grain}

                find_country = db1.find(query, {"country": 1, "loc_id": 1})

                if not find_country:
                    response = {"status": 'val_error', "message": {"country": ["Please assign a grain first"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

                find_country_list = list(find_country)
                total_country = len(find_country_list)

                # Convert ObjectId to string
                for item in find_country_list:
                    item["_id"] = str(item["_id"])

                response = {"status": 'success', "data": find_country_list, "total_country": total_country,
                            "message": "All country fetched successfully"}

                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200

        finally:
            stop_and_check_mongo_status(conn)


class FetchGrainVariant(MethodView):
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

            required_fields = ["grain", "c_id", "r_id"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                response = {"status": 'val_error',
                            "message": {"Details": [f"{field} is required"] for field in missing_fields}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

            grain, c_id, r_id = data["grain"], data["c_id"], data["r_id"]

            if not grain or not c_id or not r_id:
                response = {"status": 'val_error', "message": {"Details": ["Please enter all details"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

            else:
                query = {"status": "active", "type_id": "grain_variant_assign", "grain": grain, "c_id": c_id,
                         "r_id": r_id, "approve_status": {"$nin": ["pending"]}}

                find_grain_variant = db1.find(query, {"grain_variant": 1, "status": 1, "approve_status": 1}).sort(
                    "grain_variant", 1)

                find_grain_variant_list = list(find_grain_variant)

                if not find_grain_variant_list:
                    response = {"status": 'val_error', "message": {"Details": ["Please assign a grain variant"]}}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400

                total_grain_variant = len(find_grain_variant_list)

                for item in find_grain_variant_list:
                    item["_id"] = str(item["_id"])

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


fetch_grain = FetchGrain.as_view('fetch_grain_view')
fetch_country = FetchCountryBasedOnGrain.as_view('fetch_country_view')
fetch_grain_variant = FetchGrainVariant.as_view('fetch_grain_variant_view')

user.add_url_rule('/user/fetch_grain', view_func=fetch_grain, methods=['POST'])
user.add_url_rule('/user/fetch_country', view_func=fetch_country, methods=['POST'])
user.add_url_rule('/user/fetch_grain_variant', view_func=fetch_grain_variant, methods=['POST'])
