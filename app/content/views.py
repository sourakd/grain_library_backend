import datetime as dt

from bson import ObjectId
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from marshmallow.exceptions import ValidationError

from app.content.content_validation import StoryUploadSchema, CulinaryUploadSchema, EcoRegionUploadSchema, \
    PostHarvestMorphologyUploadSchema, PreHarvestMorphologyUploadSchema, AgronomyUploadSchema
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

                    status = "pending"
                    type_id = "story"

                    # Check if the story already exists
                    existing_story = db1.find_one({"type_id": "story", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_story:
                        response = {"message": {"Details": ["Story already exists"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    data = {
                        "story": story,
                        "g_v_id": g_v_id,
                        "conserved_by": conserved_by,
                        "pic_one": pic_one,
                        "pic_two": pic_two,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
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
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        try:
                            file_url1 = s3_uploader.upload_file(pic_one, type_id="story", status="pending")
                            file_url2 = s3_uploader.upload_file(pic_two, type_id="story", status="pending")
                            file_url = [file_url1, file_url2]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_story(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Insert the data into the database
                        validated_data["pic_one"] = file_url1
                        validated_data["pic_two"] = file_url2
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)

                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        # validated_data["s3_total_files"] = total_files
                        # validated_data["s3_all_folders"] = all_folders

                        response = {"message": "Story uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class PreHarvestMorphologyUpload(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = dict(request.form)
                g_v_id = data["g_v_id"].lower()
                plant_height = data["plant_height"]
                aroma = data["aroma"]
                culm_internode_colour = data["culm_internode_colour"]
                leaf_blade_colour = data["leaf_blade_colour"]
                leaf_blade_pubescence = data["leaf_blade_pubescence"]
                flag_leaf_angle = data["flag_leaf_angle"]
                flag_leaf_length = data["flag_leaf_length"]
                flag_leaf_width = data["flag_leaf_width"]
                ligule_shape = data["ligule_shape"]
                ligule_colour = data["ligule_colour"]
                pic_one = request.files.get("pic_one")
                pic_two = request.files.get("pic_two")

                if g_v_id and plant_height and aroma and culm_internode_colour and leaf_blade_colour and leaf_blade_pubescence and flag_leaf_angle and flag_leaf_length and flag_leaf_width and ligule_shape and ligule_colour and pic_one and pic_two:

                    status = "pending"
                    type_id = "pre_harvest_morphology"

                    # Check if the pre harvest morphology already exists
                    existing_pre_harvest_morphology = db1.find_one(
                        {"type_id": "pre_harvest_morphology", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_pre_harvest_morphology:
                        response = {"message": {"Details": ["Pre Harvest Morphology already exists"]},
                                    "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    data = {
                        "g_v_id": g_v_id,
                        "plant_height": plant_height,
                        "aroma": aroma,
                        "culm_internode_colour": culm_internode_colour,
                        "leaf_blade_colour": leaf_blade_colour,
                        "leaf_blade_pubescence": leaf_blade_pubescence,
                        "flag_leaf_angle": flag_leaf_angle,
                        "flag_leaf_length": flag_leaf_length,
                        "flag_leaf_width": flag_leaf_width,
                        "ligule_shape": ligule_shape,
                        "ligule_colour": ligule_colour,
                        "pic_one": pic_one,
                        "pic_two": pic_two,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
                    }
                    try:
                        validated_data = PreHarvestMorphologyUploadSchema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        try:
                            file_url1 = s3_uploader.upload_file(pic_one, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url2 = s3_uploader.upload_file(pic_two, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url = [file_url1, file_url2]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_content(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["pic_one"] = file_url1
                        validated_data["pic_two"] = file_url2
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)
                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        # validated_data["s3_total_files"] = total_files
                        # validated_data["s3_all_folders"] = all_folders

                        response = {"message": "Pre Harvest Morphology uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class PostHarvestMorphologyUpload(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = dict(request.form)
                g_v_id = data["g_v_id"].lower()
                panicle_length = data["panicle_length"].lower()
                panicle_threshability = data["panicle_threshability"].lower()
                panicle_type = data["panicle_type"].lower()
                awning_length = data["awning_length"].lower()
                awning_colour = data["awning_colour"].lower()
                grain_weight = data["grain_weight"].lower()
                lemma_palea_colour = data["lemma_palea_colour"].lower()
                lemma_palea_hair = data["lemma_palea_hair"].lower()
                grain_length = data["grain_length"].lower()
                grain_width = data["grain_width"].lower()
                kernel_colour = data["kernel_colour"].lower()
                kernel_length = data["kernel_length"].lower()
                kernel_width = data["kernel_width"].lower()
                pic_one = request.files.get("pic_one")
                pic_two = request.files.get("pic_two")

                if g_v_id and panicle_length and panicle_threshability and panicle_type and awning_length and awning_colour and grain_weight and lemma_palea_colour and lemma_palea_hair and grain_length and grain_width and kernel_colour and kernel_length and kernel_width and pic_one and pic_two:
                    status = "pending"
                    type_id = "post_harvest_morphology"

                    # Check if the post harvest morphology already exists
                    existing_post_harvest_morphology = db1.find_one(
                        {"type_id": "post_harvest_morphology", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_post_harvest_morphology:
                        response = {"message": {"Details": ["Post Harvest Morphology already exists"]},
                                    "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    data = {
                        "g_v_id": g_v_id,
                        "panicle_length": panicle_length,
                        "panicle_threshability": panicle_threshability,
                        "panicle_type": panicle_type,
                        "awning_length": awning_length,
                        "awning_colour": awning_colour,
                        "grain_weight": grain_weight,
                        "lemma_palea_colour": lemma_palea_colour,
                        "lemma_palea_hair": lemma_palea_hair,
                        "grain_length": grain_length,
                        "grain_width": grain_width,
                        "kernel_colour": kernel_colour,
                        "kernel_length": kernel_length,
                        "kernel_width": kernel_width,
                        "pic_one": pic_one,
                        "pic_two": pic_two,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
                    }
                    try:
                        validated_data = PostHarvestMorphologyUploadSchema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        try:
                            file_url1 = s3_uploader.upload_file(pic_one, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url2 = s3_uploader.upload_file(pic_two, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url = [file_url1, file_url2]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_story(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["pic_one"] = file_url1
                        validated_data["pic_two"] = file_url2
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)
                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        # validated_data["s3_total_files"] = total_files
                        # validated_data["s3_all_folders"] = all_folders

                        response = {"message": "Post Harvest Morphology uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class EcoRegionUpload(MethodView):

    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = dict(request.form)
                eco_region_img = request.files.get("eco_region_img")
                eco_region_link = data["eco_region_link"]
                g_v_id = data["g_v_id"]

                if eco_region_img and eco_region_link and g_v_id:
                    status = "pending"
                    type_id = "eco_region"

                    # Check if the eco-region already exists
                    existing_eco_region = db1.find_one(
                        {"type_id": "eco_region", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_eco_region:
                        response = {"message": {"Details": ["Eco Region already exists"]},
                                    "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    # Prepare the data to be inserted into the database
                    eco_region_img_url = ""
                    data = {
                        "eco_region_img": eco_region_img,
                        "eco_region_link": eco_region_link,
                        "g_v_id": g_v_id,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
                    }
                    try:
                        validated_data = EcoRegionUploadSchema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400
                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)
                        try:
                            file_url = s3_uploader.upload_file(eco_region_img, type_id="eco_region", status="pending")
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["eco_region_img"] = file_url
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)
                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        # validated_data["s3_total_files"] = total_files
                        # validated_data["s3_all_folders"] = all_folders

                        response = {"message": "Eco Region uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class CulinaryUpload(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = dict(request.form)
                g_v_id = data["g_v_id"]
                about = data["about"]
                recipe = data["recipe"]
                pic_one = request.files.get("pic_one")
                pic_two = request.files.get("pic_two")

                if g_v_id and about and recipe and pic_one and pic_two:
                    status = "pending"
                    type_id = "culinary"
                    # Check if the culinary already exists
                    existing_culinary = db1.find_one(
                        {"type_id": "culinary", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_culinary:
                        response = {"message": {"Details": ["Culinary already exists"]},
                                    "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    # Prepare the data to be inserted into the database
                    pic_one_url = ""
                    pic_two_url = ""
                    data = {
                        "g_v_id": g_v_id,
                        "about": about,
                        "recipe": recipe,
                        "pic_one": pic_one,
                        "pic_two": pic_two,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
                    }
                    try:
                        validated_data = CulinaryUploadSchema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)

                        try:
                            file_url1 = s3_uploader.upload_file(pic_one, type_id="culinary", status="pending")
                            file_url2 = s3_uploader.upload_file(pic_two, type_id="culinary", status="pending")
                            file_urls = [file_url1, file_url2]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_content(file_urls, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["pic_one"] = file_url1
                        validated_data["pic_two"] = file_url2
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)
                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        # validated_data["s3_total_files"] = total_files
                        # validated_data["s3_all_folders"] = all_folders

                        response = {"message": "Culinary uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class AgronomyUpload(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = request.get_json()
                g_v_id = data["g_v_id"]
                seedbed_preparation = data["seedbed_preparation"]
                seed_broadcast = data["seed_broadcast"]
                field_preparation_weeding = data["field_preparation_weeding"]
                transplantation = data["transplantation"]
                tillering_starts = data["tillering_starts"]
                weeding_phase_two = data["weeding_phase_two"]
                flowering = data["flowering"]
                harvest = data["harvest"]

                if g_v_id and seedbed_preparation and seed_broadcast and field_preparation_weeding and transplantation and tillering_starts and weeding_phase_two and flowering and harvest:
                    status = "pending"
                    type_id = "agronomy"
                    # Check if the agronomy already exists
                    existing_agronomy = db1.find_one(
                        {"type_id": "agronomy", "g_v_id": g_v_id, "status": {"$ne": "delete"}})
                    if existing_agronomy:
                        response = {"message": {"Details": ["Agronomy already exists"]},
                                    "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    # Prepare the data to be inserted into the database
                    # validated_data = {}
                    # for key, value in data.items():
                    #     if value is not None:
                    #         validated_data[key] = value
                    data = {
                        "g_v_id": g_v_id,
                        "seedbed_preparation": seedbed_preparation,
                        "seed_broadcast": seed_broadcast,
                        "field_preparation_weeding": field_preparation_weeding,
                        "transplantation": transplantation,
                        "tillering_starts": tillering_starts,
                        "weeding_phase_two": weeding_phase_two,
                        "flowering": flowering,
                        "harvest": harvest,
                        "status": status,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": None,
                        "type_id": type_id
                    }
                    try:
                        validated_data = AgronomyUploadSchema.load(data)
                    except ValidationError as err:
                        response = {"message": err.messages, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    else:
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        validated_data["type_id"] = type_id
                        db1.insert_one(validated_data)
                        # Extract the _id value
                        validated_data["_id"] = str(validated_data["_id"])
                        response = {"message": "Agronomy uploaded successfully", "status": "success",
                                    "data": validated_data}
                        stop_and_check_mongo_status(conn)
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


class content_approval_update(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = request.get_json()
                content_id = data["content_id"]
                type_id = data["type_id"]
                status = data["status"]
                remarks = data["remarks"]

                if content_id and status and remarks:

                    find_content = db1.find_one({"_id": ObjectId(content_id), "type_id": type_id})

                    if find_content["status"] == "approve":
                        response = {"message": {"Details": ["Content already approved"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 400

                    if not find_content:
                        response = {"message": {"Details": ["Content not found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 404

                    else:
                        db1.update_one({"_id": ObjectId(content_id), "type_id": type_id}, {
                            "$set": {"status": status, "remarks": remarks,
                                     "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})

                        response = {"status": "success", "message": "Content updated successfully"}
                        stop_and_check_mongo_status(conn)
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


class FetchContent(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            start_and_check_mongo()
            db = database_connect_mongo()
            if db is not None:
                db1 = db["content"]
                data = request.get_json()
                type_id = data["type_id"]
                g_v_id = data["g_v_id"]

                if type_id and g_v_id:

                    content_details = db1.find_one({"g_v_id": g_v_id, "type_id": type_id})
                    if content_details:
                        content_details["_id"] = str(content_details["_id"])
                        response = {"message": "Content fetched successfully", "status": "success",
                                    "data": content_details}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"message": {"Details": ["No content found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
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


story_upload = StoryUpload.as_view('story_upload')
pre_harvest_morphology = PreHarvestMorphologyUpload.as_view('pre_harvest_morphology')
post_harvest_morphology = PostHarvestMorphologyUpload.as_view('post_harvest_morphology')
eco_region = EcoRegionUpload.as_view('eco_region')
culinary = CulinaryUpload.as_view('culinary')
agronomy = AgronomyUpload.as_view('agronomy')
content_approval_update = content_approval_update.as_view('content_approval_update')
fetch_content = FetchContent.as_view('fetch_content')

content_blueprint.add_url_rule('/content/story_upload', view_func=story_upload, methods=['POST'])
content_blueprint.add_url_rule('/content/pre_harvest_morphology', view_func=pre_harvest_morphology, methods=['POST'])
content_blueprint.add_url_rule('/content/post_harvest_morphology', view_func=post_harvest_morphology, methods=['POST'])
content_blueprint.add_url_rule('/content/eco_region', view_func=eco_region, methods=['POST'])
content_blueprint.add_url_rule('/content/culinary', view_func=culinary, methods=['POST'])
content_blueprint.add_url_rule('/content/agronomy', view_func=agronomy, methods=['POST'])
content_blueprint.add_url_rule('/content/content_approval_update', view_func=content_approval_update, methods=['POST'])
content_blueprint.add_url_rule('/content/fetch_content', view_func=fetch_content, methods=['POST'])
