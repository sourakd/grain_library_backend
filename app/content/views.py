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
                story = data.get("story", [])
                g_v_id = data["g_v_id"]
                conserved_by = data["conserved_by"]
                pic_one = request.files.get("pic_one")
                pic_two = request.files.get("pic_two")
                pic_three = request.files.get("pic_three")

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
                        "pic_three": pic_three,
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
                            file_url3 = s3_uploader.upload_file(pic_three, type_id="story", status="pending")
                            file_url = [file_url1, file_url2, file_url3]
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
                        validated_data["pic_three"] = file_url3
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
                g_v_id = data["g_v_id"]
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
                plant_height_pic = request.files.get("plant_height_pic")
                aroma_pic = request.files.get("aroma_pic")
                culm_internode_colour_pic = request.files.get("culm_internode_colour_pic")
                leaf_blade_colour_pic = request.files.get("leaf_blade_colour_pic")
                leaf_blade_pubescence_pic = request.files.get("leaf_blade_pubescence_pic")
                flag_leaf_angle_pic = request.files.get("flag_leaf_angle_pic")
                flag_leaf_length_pic = request.files.get("flag_leaf_length_pic")
                flag_leaf_width_pic = request.files.get("flag_leaf_width_pic")
                ligule_shape_pic = request.files.get("ligule_shape_pic")
                ligule_colour_pic = request.files.get("ligule_colour_pic")

                if (g_v_id and plant_height and aroma and culm_internode_colour and leaf_blade_colour and
                        leaf_blade_pubescence and flag_leaf_angle and flag_leaf_length and flag_leaf_width and
                        ligule_shape and ligule_colour and plant_height_pic and aroma_pic and culm_internode_colour_pic and
                        leaf_blade_colour_pic and leaf_blade_pubescence_pic and flag_leaf_angle_pic and flag_leaf_length_pic and
                        flag_leaf_width_pic and ligule_shape_pic and ligule_colour_pic):

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
                        "plant_height_pic": plant_height_pic,
                        "aroma_pic": aroma_pic,
                        "culm_internode_colour_pic": culm_internode_colour_pic,
                        "leaf_blade_colour_pic": leaf_blade_colour_pic,
                        "leaf_blade_pubescence_pic": leaf_blade_pubescence_pic,
                        "flag_leaf_angle_pic": flag_leaf_angle_pic,
                        "flag_leaf_length_pic": flag_leaf_length_pic,
                        "flag_leaf_width_pic": flag_leaf_width_pic,
                        "ligule_shape_pic": ligule_shape_pic,
                        "ligule_colour_pic": ligule_colour_pic,
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
                            file_url1 = s3_uploader.upload_file(plant_height_pic, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url2 = s3_uploader.upload_file(aroma_pic, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url3 = s3_uploader.upload_file(culm_internode_colour_pic,
                                                                type_id="pre_harvest_morphology", status="pending")
                            file_url4 = s3_uploader.upload_file(leaf_blade_colour_pic,
                                                                type_id="pre_harvest_morphology", status="pending")
                            file_url5 = s3_uploader.upload_file(leaf_blade_pubescence_pic,
                                                                type_id="pre_harvest_morphology", status="pending")
                            file_url6 = s3_uploader.upload_file(flag_leaf_angle_pic, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url7 = s3_uploader.upload_file(flag_leaf_length_pic,
                                                                type_id="pre_harvest_morphology", status="pending")
                            file_url8 = s3_uploader.upload_file(flag_leaf_width_pic, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url9 = s3_uploader.upload_file(ligule_shape_pic, type_id="pre_harvest_morphology",
                                                                status="pending")
                            file_url10 = s3_uploader.upload_file(ligule_colour_pic, type_id="pre_harvest_morphology",
                                                                 status="pending")
                            file_url = [file_url1, file_url2, file_url3, file_url4, file_url5, file_url6, file_url7,
                                        file_url8, file_url9, file_url10]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_content(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["plant_height_pic"] = file_url1
                        validated_data["aroma_pic"] = file_url2
                        validated_data["culm_internode_colour_pic"] = file_url3
                        validated_data["leaf_blade_colour_pic"] = file_url4
                        validated_data["leaf_blade_pubescence_pic"] = file_url5
                        validated_data["flag_leaf_angle_pic"] = file_url6
                        validated_data["flag_leaf_length_pic"] = file_url7
                        validated_data["flag_leaf_width_pic"] = file_url8
                        validated_data["ligule_shape_pic"] = file_url9
                        validated_data["ligule_colour_pic"] = file_url10
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
                g_v_id = data["g_v_id"]
                panicle_length = data["panicle_length"]
                panicle_threshability = data["panicle_threshability"]
                panicle_type = data["panicle_type"]
                awning_length = data["awning_length"]
                awning_colour = data["awning_colour"]
                grain_weight = data["grain_weight"]
                lemma_palea_colour = data["lemma_palea_colour"]
                lemma_palea_hair = data["lemma_palea_hair"]
                grain_length = data["grain_length"]
                grain_width = data["grain_width"]
                kernel_colour = data["kernel_colour"]
                kernel_length = data["kernel_length"]
                kernel_width = data["kernel_width"]
                panicle_length_pic = request.files.get("panicle_length_pic")
                panicle_threshability_pic = request.files.get("panicle_threshability_pic")
                panicle_type_pic = request.files.get("panicle_type_pic")
                awning_length_pic = request.files.get("awning_length_pic")
                awning_colour_pic = request.files.get("awning_colour_pic")
                grain_weight_pic = request.files.get("grain_weight_pic")
                lemma_palea_colour_pic = request.files.get("lemma_palea_colour_pic")
                lemma_palea_hair_pic = request.files.get("lemma_palea_hair_pic")
                grain_length_pic = request.files.get("grain_length_pic")
                grain_width_pic = request.files.get("grain_width_pic")
                kernel_colour_pic = request.files.get("kernel_colour_pic")
                kernel_length_pic = request.files.get("kernel_length_pic")
                kernel_width_pic = request.files.get("kernel_width_pic")

                if panicle_length_pic and panicle_threshability_pic and panicle_type_pic and awning_length_pic and awning_colour_pic and grain_weight_pic and lemma_palea_colour_pic and lemma_palea_hair_pic and grain_length_pic and grain_width_pic and kernel_colour_pic and kernel_length_pic and kernel_width_pic:

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
                        "panicle_length_pic": panicle_length_pic,
                        "panicle_threshability_pic": panicle_threshability_pic,
                        "panicle_type_pic": panicle_type_pic,
                        "awning_length_pic": awning_length_pic,
                        "awning_colour_pic": awning_colour_pic,
                        "grain_weight_pic": grain_weight_pic,
                        "lemma_palea_colour_pic": lemma_palea_colour_pic,
                        "lemma_palea_hair_pic": lemma_palea_hair_pic,
                        "grain_length_pic": grain_length_pic,
                        "grain_width_pic": grain_width_pic,
                        "kernel_colour_pic": kernel_colour_pic,
                        "kernel_length_pic": kernel_length_pic,
                        "kernel_width_pic": kernel_width_pic,
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
                            file_url1 = s3_uploader.upload_file(panicle_length_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url2 = s3_uploader.upload_file(panicle_threshability_pic,
                                                                type_id="post_harvest_morphology", status="pending")
                            file_url3 = s3_uploader.upload_file(panicle_type_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url4 = s3_uploader.upload_file(awning_length_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url5 = s3_uploader.upload_file(awning_colour_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url6 = s3_uploader.upload_file(grain_weight_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url7 = s3_uploader.upload_file(lemma_palea_colour_pic,
                                                                type_id="post_harvest_morphology", status="pending")
                            file_url8 = s3_uploader.upload_file(lemma_palea_hair_pic,
                                                                type_id="post_harvest_morphology", status="pending")
                            file_url9 = s3_uploader.upload_file(grain_length_pic, type_id="post_harvest_morphology",
                                                                status="pending")
                            file_url10 = s3_uploader.upload_file(grain_width_pic, type_id="post_harvest_morphology",
                                                                 status="pending")
                            file_url11 = s3_uploader.upload_file(kernel_colour_pic, type_id="post_harvest_morphology",
                                                                 status="pending")
                            file_url12 = s3_uploader.upload_file(kernel_length_pic, type_id="post_harvest_morphology",
                                                                 status="pending")
                            file_url13 = s3_uploader.upload_file(kernel_width_pic, type_id="post_harvest_morphology",
                                                                 status="pending")
                            file_url = [file_url1, file_url2, file_url3, file_url4, file_url5, file_url6, file_url7,
                                        file_url8, file_url9, file_url10, file_url11, file_url12, file_url13]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_story(file_url, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400
                        # Insert the data into the database
                        validated_data["panicle_length_pic"] = file_url1
                        validated_data["panicle_threshability_pic"] = file_url2
                        validated_data["panicle_type_pic"] = file_url3
                        validated_data["awning_length_pic"] = file_url4
                        validated_data["awning_colour_pic"] = file_url5
                        validated_data["grain_weight_pic"] = file_url6
                        validated_data["lemma_palea_colour_pic"] = file_url7
                        validated_data["lemma_palea_hair_pic"] = file_url8
                        validated_data["grain_length_pic"] = file_url9
                        validated_data["grain_width_pic"] = file_url10
                        validated_data["kernel_colour_pic"] = file_url11
                        validated_data["kernel_length_pic"] = file_url12
                        validated_data["kernel_width_pic"] = file_url13
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
                recipe = data.get("recipe", [])
                about = data.get("about", [])
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
                data = dict(request.form)
                g_v_id = data["g_v_id"]
                seedbed_preparation_weeding = data["seedbed_preparation_weeding"]
                seed_broadcast = data["seed_broadcast"]
                field_preparation_weeding = data["field_preparation_weeding"]
                transplantation = data["transplantation"]
                tillering_starts = data["tillering_starts"]
                weeding_phase_two = data["weeding_phase_two"]
                flowering = data["flowering"]
                harvest = data["harvest"]
                seedbed_preparation_pic = request.files.get("seedbed_preparation_pic")
                seed_broadcast_pic = request.files.get("seed_broadcast_pic")
                field_preparation_weeding_pic = request.files.get("field_preparation_weeding_pic")
                transplantation_pic = request.files.get("transplantation_pic")
                tillering_starts_pic = request.files.get("tillering_starts_pic")
                weeding_phase_two_pic = request.files.get("weeding_phase_two_pic")
                flowering_pic = request.files.get("flowering_pic")
                harvest_pic = request.files.get("harvest_pic")

                if g_v_id and seedbed_preparation_weeding and seed_broadcast and field_preparation_weeding and transplantation and tillering_starts and weeding_phase_two and flowering and harvest and seedbed_preparation_pic and seed_broadcast_pic and field_preparation_weeding_pic and transplantation_pic and tillering_starts_pic and weeding_phase_two_pic and flowering_pic and harvest_pic:

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
                        "seedbed_preparation_weeding": seedbed_preparation_weeding,
                        "seed_broadcast": seed_broadcast,
                        "field_preparation_weeding": field_preparation_weeding,
                        "transplantation": transplantation,
                        "tillering_starts": tillering_starts,
                        "weeding_phase_two": weeding_phase_two,
                        "flowering": flowering,
                        "harvest": harvest,
                        "seedbed_preparation_pic": seedbed_preparation_pic,
                        "seed_broadcast_pic": seed_broadcast_pic,
                        "field_preparation_weeding_pic": field_preparation_weeding_pic,
                        "transplantation_pic": transplantation_pic,
                        "tillering_starts_pic": tillering_starts_pic,
                        "weeding_phase_two_pic": weeding_phase_two_pic,
                        "flowering_pic": flowering_pic,
                        "harvest_pic": harvest_pic,
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

                        # Update the updated_at field
                        validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        s3_config = S3Config()
                        bucket_status, total_files, all_folders = s3_config.connect_to_s3()
                        s3_uploader = S3Uploader(s3_config)

                        try:
                            file_url1 = s3_uploader.upload_file(seedbed_preparation_pic, type_id="agronomy",
                                                                status="pending")
                            file_url2 = s3_uploader.upload_file(seed_broadcast_pic, type_id="agronomy",
                                                                status="pending")
                            file_url3 = s3_uploader.upload_file(field_preparation_weeding_pic, type_id="agronomy",
                                                                status="pending")
                            file_url4 = s3_uploader.upload_file(transplantation_pic, type_id="agronomy",
                                                                status="pending")
                            file_url5 = s3_uploader.upload_file(tillering_starts_pic, type_id="agronomy",
                                                                status="pending")
                            file_url6 = s3_uploader.upload_file(weeding_phase_two_pic, type_id="agronomy",
                                                                status="pending")
                            file_url7 = s3_uploader.upload_file(flowering_pic, type_id="agronomy", status="pending")
                            file_url8 = s3_uploader.upload_file(harvest_pic, type_id="agronomy", status="pending")
                            file_urls = [file_url1, file_url2, file_url3, file_url4, file_url5, file_url6, file_url7,
                                         file_url8]
                        except Exception as e:
                            response = {"message": str(e), "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        if s3_uploader.check_existing_file_content(file_urls, type_id):
                            response = {"message": {"File": ["File already exist"]}, "status": "val_error"}
                            stop_and_check_mongo_status(conn)
                            return make_response(jsonify(response)), 400

                        # Insert the data into the database

                        validated_data["seedbed_preparation_pic"] = file_url1
                        validated_data["seed_broadcast_pic"] = file_url2
                        validated_data["field_preparation_weeding_pic"] = file_url3
                        validated_data["transplantation_pic"] = file_url4
                        validated_data["tillering_starts_pic"] = file_url5
                        validated_data["weeding_phase_two_pic"] = file_url6
                        validated_data["flowering_pic"] = file_url7
                        validated_data["harvest_pic"] = file_url8
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
                db2 = db["grain_assign"]
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

                    g_v_id = find_content["g_v_id"]

                    grain_variant = db2.find_one({"_id": ObjectId(g_v_id), "status": "active"})

                    if not grain_variant:
                        response = {"message": {"Details": ["Grain variant not found"]}, "status": "val_error"}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 404

                    else:

                        approve_status = grain_variant["approve_status"]
                        print(approve_status)

                        db1.update_one({"_id": ObjectId(content_id), "type_id": type_id}, {
                            "$set": {"status": status, "remarks": remarks,
                                     "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})

                        if approve_status == "pending":
                            db2.update_one(
                                {"_id": ObjectId(g_v_id), "status": "active"},
                                {"$set": {"approve_status": [type_id],
                                          "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                            )

                        else:
                            db2.update_one(
                                {"_id": ObjectId(g_v_id), "status": "active"},
                                {"$addToSet": {"approve_status": type_id},
                                 "$set": {"updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                            )

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
                status = data["status"]

                if type_id and g_v_id and status:

                    content_details = db1.find_one({"g_v_id": g_v_id, "type_id": type_id, "status": status})
                    if content_details:
                        content_details["_id"] = str(content_details["_id"])
                        response = {"message": "Content fetched successfully", "status": "success",
                                    "data": content_details}
                        stop_and_check_mongo_status(conn)
                        return make_response(jsonify(response)), 200
                    else:
                        response = {"message": {"Details": ["No content found"]}, "status": "val_error"}
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
