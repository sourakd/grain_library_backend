import datetime as dt

from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError

from app.content.content_validation import StoryUploadSchema
from app.helpers import S3Uploader
from db_connection import start_and_check_mongo, database_connect_mongo, stop_and_check_mongo_status, conn
from settings.configuration import S3Config

content_blueprint = Blueprint('content', __name__)


class StoryUpload(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = dict(request.form)
                story = data["story"]
                g_v_id = data["g_v_id"].lower()
                conserved_by = data["conserved_by"].lower()
                pic_one = request.files.get("pic_one")
                pic_two = request.files.get("pic_two")

                if story and g_v_id and conserved_by and pic_one and pic_two:

                    data = {
                        "story": story,
                        "g_v_id": g_v_id,
                        "conserved_by": conserved_by,
                        "pic_one": pic_one,
                        "pic_two": pic_two,
                        "status": "active",
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                    }

                    try:
                        validated_data = StoryUploadSchema.load(data)
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
                        file_url1 = s3_uploader.upload_file(pic_one)
                        file_url2 = s3_uploader.upload_file(pic_two)
                        file_url = [file_url1, file_url2]

                        if s3_uploader.check_existing_file_story(file_url):
                            response = {"message": "File already exist", "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Insert the data into the database
                        validated_data["pic_one"] = file_url1
                        validated_data["pic_two"] = file_url2
                        db1.insert_one(validated_data)

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])

                        response = {"message": "Story uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                else:
                    response = {"message": "All fields are required"}
                    stop_and_check_mongo_status(conn)
                    return make_response(jsonify(response)), 400
            else:
                response = {"message": "Database connection failed"}
                stop_and_check_mongo_status(conn)
                return make_response(jsonify(response)), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            stop_and_check_mongo_status(conn)
            return make_response(jsonify(response)), 400


story_upload = StoryUpload.as_view('story_upload')
content_blueprint.add_url_rule('/content/story_upload', view_func=story_upload, methods=['POST'])
