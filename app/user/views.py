from flask import make_response, jsonify, Blueprint
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
                                      {"grain": 1, "grain_assign_id": 1})
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
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": {"Details": ["Database connection failed"]}}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 200


fetch_grain = FetchGrain.as_view('fetch_grain_view')

user.add_url_rule('/user/fetch_grain', view_func=fetch_grain, methods=['POST'])
