import re

from bson import ObjectId
from marshmallow import Schema, fields, validates, ValidationError
from werkzeug.datastructures import FileStorage as File

from db_connection import database_connect_mongo


class StoryUpload(Schema):
    story = fields.Str(required=True)
    g_v_id = fields.Str(required=True)
    conserved_by = fields.Str(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)

    @validates('story')
    # self = story
    def validate_story(self, value):
        if not value:
            raise ValidationError('Story is required')
        elif len(re.findall(r'\b\w+\b', value)) < 5:
            raise ValidationError('Story must be at least 500 words')
        elif len(re.findall(r'\b\w+\b', value)) > 10:
            raise ValidationError('Story must not exceed 600 words')

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('conserved_by')
    def validate_conserved_by(self, value):
        if not value:
            raise ValidationError('Conserved by is required')

    @validates('pic_one')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Picture one is required')
        if not isinstance(value, File):
            raise ValidationError('Picture one must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture one must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 500 * 1024:
            raise ValidationError('Picture one must be between 300KB and 500KB')

    @validates('pic_two')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Picture two is required')
        if not isinstance(value, File):
            raise ValidationError('Picture two must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture two must be between 300KB and 500KB')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "story":
            raise ValidationError('Type ID must be story')


class PreHarvestMorphologyUpload(Schema):
    g_v_id = fields.Str(required=True)
    plant_height = fields.Str(required=True)
    aroma = fields.Str(required=True)
    culm_internode_colour = fields.Str(required=True)
    leaf_blade_colour = fields.Str(required=True)
    leaf_blade_pubescence = fields.Str(required=True)
    flag_leaf_angle = fields.Str(required=True)
    flag_leaf_length = fields.Str(required=True)
    flag_leaf_width = fields.Str(required=True)
    ligule_shape = fields.Str(required=True)
    ligule_colour = fields.Str(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)
    status = fields.Str(required=True)

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('plant_height')
    def validate_plant_height(self, value):
        if not value:
            raise ValidationError('Plant height is required')
        if not isinstance(value, str):
            raise ValidationError('Plant height must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Plant height must contain only numeric characters and a single dot')

    @validates('aroma')
    def validate_aroma(self, value):
        if not value:
            raise ValidationError('Aroma is required')
        if not isinstance(value, str):
            raise ValidationError('Aroma must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Aroma must contain only alphabets and spaces')

    @validates('culm_internode_colour')
    def validate_culm_internode_colour(self, value):
        if not value:
            raise ValidationError('Culm internode colour is required')
        if not isinstance(value, str):
            raise ValidationError('Culm internode colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Culm internode colour must contain only alphabets and spaces')

    @validates('leaf_blade_colour')
    def validate_leaf_blade_colour(self, value):
        if not value:
            raise ValidationError('Leaf blade colour is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Leaf blade colour must contain only alphabets and spaces')

    @validates('leaf_blade_pubescence')
    def validate_leaf_blade_pubescence(self, value):
        if not value:
            raise ValidationError('Leaf blade pubescence is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade pubescence must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Leaf blade pubescence must contain only alphabets and spaces')

    @validates('flag_leaf_angle')
    def validate_flag_leaf_angle(self, value):
        if not value:
            raise ValidationError('Flag leaf angle is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf angle must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Flag leaf angle must contain only alphabets and spaces')

    @validates('flag_leaf_length')
    def validate_flag_leaf_length(self, value):
        if not value:
            raise ValidationError('Flag leaf length is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf length must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Flag leaf length must contain only numeric characters and a single dot')

    @validates('flag_leaf_width')
    def validate_flag_leaf_width(self, value):
        if not value:
            raise ValidationError('Flag leaf width is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf width must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Flag leaf width must contain only numeric characters and a single dot')

    @validates('ligule_shape')
    def validate_ligule_shape(self, value):
        if not value:
            raise ValidationError('Ligule shape is required')
        if not isinstance(value, str):
            raise ValidationError('Ligule shape must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Ligule shape must contain only alphabets and spaces')

    @validates('ligule_colour')
    def validate_ligule_colour(self, value):
        if not value:
            raise ValidationError('Ligule colour is required')
        if not isinstance(value, str):
            raise ValidationError('Ligule colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Ligule colour must contain only alphabets and spaces')

    @validates('pic_one')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Picture one is required')
        if not isinstance(value, File):
            raise ValidationError('Picture one must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture one must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 500 * 1024:
            raise ValidationError('Picture one must be between 300KB and 500KB')

    @validates('pic_two')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Picture two is required')
        if not isinstance(value, File):
            raise ValidationError('Picture two must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture two must be between 300KB and 500KB')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "pre_harvest_morphology":
            raise ValidationError('Type ID must be pre_harvest_morphology')


class PostHarvestMorphologyUpload(Schema):
    g_v_id = fields.Str(required=True)
    plant_height = fields.Str(required=True)
    aroma = fields.Str(required=True)
    culm_internode_colour = fields.Str(required=True)
    leaf_blade_colour = fields.Str(required=True)
    leaf_blade_pubescence = fields.Str(required=True)
    flag_leaf_angle = fields.Str(required=True)
    flag_leaf_length = fields.Str(required=True)
    flag_leaf_width = fields.Str(required=True)
    ligule_shape = fields.Str(required=True)
    ligule_colour = fields.Str(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)
    status = fields.Str(required=True)

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('plant_height')
    def validate_plant_height(self, value):
        if not value:
            raise ValidationError('Plant height is required')
        if not isinstance(value, str):
            raise ValidationError('Plant height must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Plant height must contain only numeric characters and a single dot')

    @validates('aroma')
    def validate_aroma(self, value):
        if not value:
            raise ValidationError('Aroma is required')
        if not isinstance(value, str):
            raise ValidationError('Aroma must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Aroma must contain only alphabets and spaces')

    @validates('culm_internode_colour')
    def validate_culm_internode_colour(self, value):
        if not value:
            raise ValidationError('Culm internode colour is required')
        if not isinstance(value, str):
            raise ValidationError('Culm internode colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Culm internode colour must contain only alphabets and spaces')

    @validates('leaf_blade_colour')
    def validate_leaf_blade_colour(self, value):
        if not value:
            raise ValidationError('Leaf blade colour is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Leaf blade colour must contain only alphabets and spaces')

    @validates('leaf_blade_pubescence')
    def validate_leaf_blade_pubescence(self, value):
        if not value:
            raise ValidationError('Leaf blade pubescence is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade pubescence must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Leaf blade pubescence must contain only alphabets and spaces')

    @validates('flag_leaf_angle')
    def validate_flag_leaf_angle(self, value):
        if not value:
            raise ValidationError('Flag leaf angle is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf angle must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Flag leaf angle must contain only alphabets and spaces')

    @validates('flag_leaf_length')
    def validate_flag_leaf_length(self, value):
        if not value:
            raise ValidationError('Flag leaf length is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf length must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Flag leaf length must contain only numeric characters and a single dot')

    @validates('flag_leaf_width')
    def validate_flag_leaf_width(self, value):
        if not value:
            raise ValidationError('Flag leaf width is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf width must be a string')
        if not re.match(r'^\d+(?:\.\d+)?$', value):
            raise ValidationError('Flag leaf width must contain only numeric characters and a single dot')

    @validates('ligule_shape')
    def validate_ligule_shape(self, value):
        if not value:
            raise ValidationError('Ligule shape is required')
        if not isinstance(value, str):
            raise ValidationError('Ligule shape must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Ligule shape must contain only alphabets and spaces')

    @validates('ligule_colour')
    def validate_ligule_colour(self, value):
        if not value:
            raise ValidationError('Ligule colour is required')
        if not isinstance(value, str):
            raise ValidationError('Ligule colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Ligule colour must contain only alphabets and spaces')

    @validates('pic_one')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Picture one is required')
        if not isinstance(value, File):
            raise ValidationError('Picture one must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture one must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 500 * 1024:
            raise ValidationError('Picture one must be between 300KB and 500KB')

    @validates('pic_two')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Picture two is required')
        if not isinstance(value, File):
            raise ValidationError('Picture two must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture two must be between 300KB and 500KB')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "post_harvest_morphology":
            raise ValidationError('Type ID must be post_harvest_morphology')


class EcoRegionUpload(Schema):
    eco_region_img = fields.Raw(required=True)
    eco_region_link = fields.Str(required=True)
    g_v_id = fields.Str(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('eco_region_img')
    def validate_eco_region_img(self, value):
        if not value:
            raise ValidationError('Eco region image is required')
        if not isinstance(value, File):
            raise ValidationError('Eco region image must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Eco region image must be between 300KB and 500KB')

    @validates('eco_region_link')
    def validate_eco_region_link(self, value):
        if not value:
            raise ValidationError('Eco region link is required')
        if not isinstance(value, str):
            raise ValidationError('Eco region link must be a string')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "eco_region":
            raise ValidationError('Type ID must be eco_region')


class CulinaryUpload(Schema):
    g_v_id = fields.Str(required=True)
    about = fields.Str(required=True)
    recipe = fields.Str(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('about')
    def validate_about(self, value):
        if not value:
            raise ValidationError('About is required')
        elif len(re.findall(r'\b\w+\b', value)) < 5:
            raise ValidationError('About must be at least 500 words')
        elif len(re.findall(r'\b\w+\b', value)) > 10:
            raise ValidationError('About must not exceed 600 words')

    @validates('recipe')
    def validate_recipe(self, value):
        if not value:
            raise ValidationError('Recipe is required')
        elif len(re.findall(r'\b\w+\b', value)) < 5:
            raise ValidationError('Recipe must be at least 500 words')
        elif len(re.findall(r'\b\w+\b', value)) > 10:
            raise ValidationError('Recipe must not exceed 600 words')

    @validates('pic_one')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Picture one is required')
        if not isinstance(value, File):
            raise ValidationError('Picture one must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture one must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture one must be between 300KB and 500KB')

    @validates('pic_two')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Picture two is required')
        if not isinstance(value, File):
            raise ValidationError('Picture two must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture two must be between 300KB and 500KB')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "culinary":
            raise ValidationError('Type ID must be culinary')


class AgronomyUpload(Schema):
    g_v_id = fields.Str(required=True)
    seedbed_preparation = fields.Str(required=True)
    seed_broadcast = fields.Str(required=True)
    field_preparation_weeding = fields.Str(required=True)
    transplantation = fields.Str(required=True)
    tillering_starts = fields.Str(required=True)
    weeding_phase_two = fields.Str(required=True)
    flowering = fields.Str(required=True)
    harvest = fields.Str(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)

    @validates('g_v_id')
    def validate_g_v_id(self, value):
        db = database_connect_mongo()
        db1 = db["grain_assign"]

        find_grain_variant = db1.find_one(
            {"_id": ObjectId(value), "status": "active", "type_id": "grain_variant_assign"})
        if not find_grain_variant:
            raise ValidationError('Grain variant not found')

    @validates('seedbed_preparation')
    def validate_seedbed_preparation(self, value):
        if not value:
            raise ValidationError('Seedbed preparation is required')
        elif len(re.findall(r'\b\w+\b', value)) < 5:
            raise ValidationError('Seedbed preparation must be at least 500 words')
        elif len(re.findall(r'\b\w+\b', value)) > 10:
            raise ValidationError('Seedbed preparation must not exceed 600 words')

    @validates('seed_broadcast')
    def validate_seed_broadcast(self, value):
        if not value:
            raise ValidationError('Seed broadcast is required')

    @validates('field_preparation_weeding')
    def validate_field_preparation_weeding(self, value):
        if not value:
            raise ValidationError('Field preparation weeding is required')

    @validates('transplantation')
    def validate_transplantation(self, value):
        if not value:
            raise ValidationError('Transplantation is required')

    @validates('tillering_starts')
    def validate_tillering_starts(self, value):
        if not value:
            raise ValidationError('Tillering starts is required')

    @validates('weeding_phase_two')
    def validate_weeding_phase_two(self, value):
        if not value:
            raise ValidationError('Weeding phase two is required')

    @validates('flowering')
    def validate_flowering(self, value):
        if not value:
            raise ValidationError('Flowering is required')

    @validates('harvest')
    def validate_harvest(self, value):
        if not value:
            raise ValidationError('Harvest is required')

    @validates('status')
    def validate_status(self, value):
        if not value:
            raise ValidationError('Status is required')
        if value != "pending":
            raise ValidationError('Status must be pending')

    @validates('type_id')
    def validate_type_id(self, value):
        if not value:
            raise ValidationError('Type ID is required')
        if value != "agronomy":
            raise ValidationError('Type ID must be agronomy')


StoryUploadSchema = StoryUpload()
PreHarvestMorphologyUploadSchema = PreHarvestMorphologyUpload()
PostHarvestMorphologyUploadSchema = PostHarvestMorphologyUpload()
EcoRegionUploadSchema = EcoRegionUpload()
CulinaryUploadSchema = CulinaryUpload()
AgronomyUploadSchema = AgronomyUpload()
