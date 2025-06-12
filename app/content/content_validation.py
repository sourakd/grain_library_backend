import re

from bson import ObjectId
from marshmallow import Schema, fields, validates, ValidationError
from werkzeug.datastructures import FileStorage as File

from db_connection import database_connect_mongo


class StoryUpload(Schema):
    story = fields.Raw(required=True)
    g_v_id = fields.Str(required=True)
    conserved_by = fields.Str(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=True)
    pic_three = fields.Raw(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)

    @validates('story')
    # self = story
    def validate_story(self, value):
        if not value:
            raise ValidationError('Story is required')

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

        if file_size < 300 * 1024 or file_size > 1024 * 1024:
            raise ValidationError('Picture one must be between 300KB and 1MB')

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

        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture two must be between 300KB and 1MB')

    @validates('pic_three')
    def validate_pic_three(self, value):
        if not value:
            raise ValidationError('Picture three is required')
        if not isinstance(value, File):
            raise ValidationError('Picture three must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture three must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture three must be between 300KB and 1MB')

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
    culm_internode_colour = fields.Str(required=True)
    leaf_blade_colour = fields.Str(required=True)
    leaf_blade_length = fields.Str(required=False)
    leaf_blade_width = fields.Str(required=True)
    flag_leaf_angle = fields.Str(required=True)
    ligule_shape = fields.Str(required=True)
    ligule_length = fields.Str(required=True)
    ligule_colour = fields.Str(required=True)
    collar_colour = fields.Str(required=True)
    panicle_length = fields.Str(required=True)
    panicle_axis = fields.Str(required=True)
    panicle_type = fields.Str(required=True)
    panicle_exertion = fields.Str(required=True)

    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    type_id = fields.Str(required=True)
    status = fields.Str(required=True)

    plant_height_pic = fields.Raw(required=True)
    culm_internode_colour_pic = fields.Raw(required=True)
    leaf_blade_colour_pic = fields.Raw(required=True)
    leaf_blade_length_pic = fields.Raw(required=True)
    leaf_blade_width_pic = fields.Raw(required=True)
    flag_leaf_angle_pic = fields.Raw(required=True)
    ligule_shape_pic = fields.Raw(required=True)
    ligule_length_pic = fields.Raw(required=True)
    ligule_colour_pic = fields.Raw(required=True)
    collar_colour_pic = fields.Raw(required=True)
    panicle_length_pic = fields.Raw(required=True)
    panicle_axis_pic = fields.Raw(required=True)
    panicle_type_pic = fields.Raw(required=True)
    panicle_exertion_pic = fields.Raw(required=True)

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

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Plant height must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in plant height')

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

    @validates('leaf_blade_length')
    def validate_leaf_blade_length(self, value):
        if not value:
            raise ValidationError('Leaf blade length is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Leaf blade length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Leaf blade length')

    @validates('leaf_blade_width')
    def validate_leaf_blade_width(self, value):
        if not value:
            raise ValidationError('Leaf blade width is required')
        if not isinstance(value, str):
            raise ValidationError('Leaf blade width must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Leaf blade width must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Leaf blade width')

    @validates('flag_leaf_angle')
    def validate_flag_leaf_angle(self, value):
        if not value:
            raise ValidationError('Flag leaf angle is required')
        if not isinstance(value, str):
            raise ValidationError('Flag leaf angle must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Flag leaf angle must contain only alphabets and spaces')

    @validates('ligule_length')
    def validate_ligule_length(self, value):
        if not value:
            raise ValidationError('Ligule length is required')
        if not isinstance(value, str):
            raise ValidationError('Ligule length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Ligule length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Ligule length')

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

    @validates('collar_colour')
    def validate_collar_colour(self, value):
        if not value:
            raise ValidationError('Collar colour is required')
        if not isinstance(value, str):
            raise ValidationError('Collar colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Collar colour must contain only alphabets and spaces')

    @validates('panicle_length')
    def validate_panicle_length(self, value):
        if not value:
            raise ValidationError('Panicle length is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Panicle length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Panicle length')

    @validates('panicle_axis')
    def validate_panicle_axis(self, value):
        if not value:
            raise ValidationError('Panicle axis is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle axis must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Panicle axis must contain only alphabets and spaces')

    @validates('panicle_type')
    def validate_panicle_type(self, value):
        if not value:
            raise ValidationError('Panicle type is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle type must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Panicle type must contain only alphabets and spaces')

    @validates('panicle_exertion')
    def validate_panicle_exertion(self, value):
        if not value:
            raise ValidationError('Panicle exertion is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle exertion must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Panicle exertion must contain only alphabets and spaces')

    @validates('plant_height_pic')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Picture of plant height is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of plant height must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of plant height must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 1024 * 1024:
            raise ValidationError('Picture of plant height must be between 300KB and 1MB')

    @validates('leaf_blade_width_pic')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Picture of leaf blade width is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of leaf blade width must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of leaf blade width must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 1024 * 1024:
            raise ValidationError('Picture of leaf blade width must be between 300KB and 1MB')

    @validates('leaf_blade_length_pic')
    def validate_pic_three(self, value):
        if not value:
            raise ValidationError('Picture of leaf blade length is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of leaf blade length must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of leaf blade length must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size < 300 * 1024 or file_size > 1024 * 1024:
            raise ValidationError('Picture of leaf blade length must be between 300KB and 1MB')

    @validates('culm_internode_colour_pic')
    def validate_pic_four(self, value):
        if not value:
            raise ValidationError('Picture of culm internode colour is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of culm internode colour must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of culm internode colour must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of culm internode colour must be between 300KB and 1MB')

    @validates('leaf_blade_colour_pic')
    def validate_pic_five(self, value):
        if not value:
            raise ValidationError('Picture of leaf blade colour is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of leaf blade colour must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of leaf blade colour must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of leaf blade colour must be between 300KB and 1MB')

    @validates('ligule_colour_pic')
    def validate_pic_six(self, value):
        if not value:
            raise ValidationError('Picture of ligule colour is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of ligule colour must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of ligule colour must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of ligule colour must be between 300KB and 1MB')

    @validates('flag_leaf_angle_pic')
    def validate_pic_seven(self, value):
        if not value:
            raise ValidationError('Picture of flag leaf angle is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of flag leaf angle must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of flag leaf angle must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of flag leaf angle must be between 300KB and 1MB')

    @validates('ligule_shape_pic')
    def validate_pic_eight(self, value):
        if not value:
            raise ValidationError('Picture of ligule shape is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of ligule shape must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of ligule shape must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of ligule shape must be between 300KB and 1MB')

    @validates('ligule_length_pic')
    def validate_pic_nine(self, value):
        if not value:
            raise ValidationError('Picture of ligule length is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of ligule length must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of ligule length must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of ligule length must be between 300KB and 1MB')

    @validates('collar_colour_pic')
    def validate_pic_ten(self, value):
        if not value:
            raise ValidationError('Picture of collar colour is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of collar colour must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of collar colour must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of collar colour must be between 300KB and 1MB')

    @validates('panicle_length_pic')
    def validate_pic_eleven(self, value):
        if not value:
            raise ValidationError('Picture of panicle length is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of panicle length must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of panicle length must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle length must be between 300KB and 1MB')

    @validates('panicle_axis_pic')
    def validate_pic_twelve(self, value):
        if not value:
            raise ValidationError('Picture of panicle axis is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of panicle axis must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of panicle axis must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle axis must be between 300KB and 1MB')

    @validates('panicle_type_pic')
    def validate_pic_thirteen(self, value):
        if not value:
            raise ValidationError('Picture of panicle type is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of panicle type must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of panicle type must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle type must be between 300KB and 1MB')

    @validates('panicle_exertion_pic')
    def validate_pic_fourteen(self, value):
        if not value:
            raise ValidationError('Picture of panicle exertion is required')
        if not isinstance(value, File):
            raise ValidationError('Picture of panicle exertion must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture of panicle exertion must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle exertion must be between 300KB and 1MB')

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
    panicle_density = fields.Str(required=True)
    panicle_threshability = fields.Str(required=True)
    awning = fields.Str(required=True)
    awning_length = fields.Str(required=True)
    awning_colour = fields.Str(required=True)
    grain_weight = fields.Str(required=True)
    lemma_palea_colour = fields.Str(required=True)
    lemma_palea_pubescence = fields.Str(required=True)
    grain_length = fields.Str(required=True)
    grain_width = fields.Str(required=True)
    kernel_colour = fields.Str(required=True)
    kernel_length = fields.Str(required=True)
    kernel_width = fields.Str(required=True)
    scent = fields.Str(required=True)

    panicle_density_pic = fields.Raw(required=True)
    panicle_threshability_pic = fields.Raw(required=True)
    awning_pic = fields.Raw(required=True)
    awning_length_pic = fields.Raw(required=True)
    awning_colour_pic = fields.Raw(required=True)
    grain_weight_pic = fields.Raw(required=True)
    lemma_palea_colour_pic = fields.Raw(required=True)
    lemma_palea_pubescence_pic = fields.Raw(required=True)
    grain_length_pic = fields.Raw(required=True)
    grain_width_pic = fields.Raw(required=True)
    kernel_colour_pic = fields.Raw(required=True)
    kernel_length_pic = fields.Raw(required=True)
    kernel_width_pic = fields.Raw(required=True)
    scent_pic = fields.Raw(required=True)

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

    @validates('panicle_density')
    def validate_panicle_density(self, value):
        if not value:
            raise ValidationError('Panicle length is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle length must be a string')
        if not re.match(r'^\d+(?:\.\d{1,2})?$', value):
            raise ValidationError('Panicle length must contain only numeric characters and up to 2 decimal places')

    @validates('panicle_threshability')
    def validate_panicle_threshability(self, value):
        if not value:
            raise ValidationError('Panicle threshability is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle threshability must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Panicle threshability must contain only alphabets and spaces')

    @validates('awning')
    def validate_awning(self, value):
        if not value:
            raise ValidationError('Panicle type is required')
        if not isinstance(value, str):
            raise ValidationError('Panicle type must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Panicle type must contain only alphabets and spaces')

    @validates('awning_length')
    def validate_awning_length(self, value):
        if not value:
            raise ValidationError('Awning length is required')
        if not isinstance(value, str):
            raise ValidationError('Awning  length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Awning length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Awning length')

    @validates('awning_colour')
    def validate_awning_colour(self, value):
        if not value:
            raise ValidationError('Awning colour is required')
        if not isinstance(value, str):
            raise ValidationError('Awning colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Awning colour must contain only alphabets and spaces')

    @validates('grain_weight')
    def validate_grain_weight(self, value):
        if not value:
            raise ValidationError('Grain weight is required')
        if not isinstance(value, str):
            raise ValidationError('Grain weight must be a string')
        if not re.match(r'^\d+(?:\.\d{1,2})?$', value):
            raise ValidationError('Grain weight must contain only numeric characters and up to 2 decimal places')

    @validates('lemma_palea_colour')
    def validate_lemma_palea_colour(self, value):
        if not value:
            raise ValidationError('Lemma palea colour is required')
        if not isinstance(value, str):
            raise ValidationError('Lemma palea colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Lemma palea colour must contain only alphabets and spaces')

    @validates('lemma_palea_pubescence')
    def validate_lemma_palea_pubescence(self, value):
        if not value:
            raise ValidationError('Lemma palea hair is required')
        if not isinstance(value, str):
            raise ValidationError('Lemma palea hair must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Lemma palea hair must contain only alphabets and spaces')

    @validates('grain_length')
    def validate_grain_length(self, value):
        if not value:
            raise ValidationError('Grain length is required')
        if not isinstance(value, str):
            raise ValidationError('Grain  length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Grain length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Grain length')

    @validates('grain_width')
    def validate_grain_width(self, value):
        if not value:
            raise ValidationError('Grain width is required')
        if not isinstance(value, str):
            raise ValidationError('Grain  width must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Grain width must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Grain width')

    @validates('kernel_colour')
    def validate_kernel_colour(self, value):
        if not value:
            raise ValidationError('Kernel colour is required')
        if not isinstance(value, str):
            raise ValidationError('Kernel colour must be a string')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValidationError('Kernel colour must contain only alphabets and spaces')

    @validates('kernel_length')
    def validate_kernel_length(self, value):
        if not value:
            raise ValidationError('Kernel length is required')
        if not isinstance(value, str):
            raise ValidationError('Kernel length must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Kernel length must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Kernel length')

    @validates('kernel_width')
    def validate_kernel_width(self, value):
        if not value:
            raise ValidationError('Kernel width is required')
        if not isinstance(value, str):
            raise ValidationError('Kernel width must be a string')

        # Check format: number1.number2 with exactly two decimal places for both
        if not re.match(r'^\d+\.\d{2}-\d+\.\d{2}$', value):
            raise ValidationError(
                'Kernel width must be in format: number1.xx-number2.xx (where xx are two decimal places)')

        try:
            # Split the string into two numbers
            num1, num2 = map(float, value.split('-'))

            # Verify number2 is greater than number1
            if num2 <= num1:
                raise ValidationError('Second number must be greater than first number')

        except ValueError:
            raise ValidationError('Invalid number format in Kernel width')

    @validates('panicle_density_pic')
    def validate_pic_one(self, value):
        if not value:
            raise ValidationError('Panicle length picture is required')
        if not isinstance(value, File):
            raise ValidationError('Panicle length picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Panicle length picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle length must be between 300KB and 1MB')

    @validates('panicle_threshability_pic')
    def validate_pic_two(self, value):
        if not value:
            raise ValidationError('Panicle threshability picture is required')
        if not isinstance(value, File):
            raise ValidationError('Panicle threshability picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Panicle threshability picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture panicle threshability must be between 300KB and 1MB')

    @validates('awning_pic')
    def validate_pic_three(self, value):
        if not value:
            raise ValidationError('Panicle type picture is required')
        if not isinstance(value, File):
            raise ValidationError('Panicle type picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Panicle type picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of panicle type must be between 300KB and 1MB')

    @validates('awning_length_pic')
    def validate_pic_four(self, value):
        if not value:
            raise ValidationError('Awning length picture is required')
        if not isinstance(value, File):
            raise ValidationError('Awning length picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Awning length picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of awning length must be between 300KB and 1MB')

    @validates('awning_colour_pic')
    def validate_pic_five(self, value):
        if not value:
            raise ValidationError('Awning colour picture is required')
        if not isinstance(value, File):
            raise ValidationError('Awning colour picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Awning colour picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of awning colour must be between 300KB and 1MB')

    @validates('grain_weight_pic')
    def validate_pic_six(self, value):
        if not value:
            raise ValidationError('Grain weight picture is required')
        if not isinstance(value, File):
            raise ValidationError('Grain weight picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Grain weight picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of grain weight must be between 300KB and 1MB')

    @validates('lemma_palea_colour_pic')
    def validate_pic_seven(self, value):
        if not value:
            raise ValidationError('Lemma palea colour picture is required')
        if not isinstance(value, File):
            raise ValidationError('Lemma palea colour picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Lemma palea colour picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of lemma palea colour must be between 300KB and 1MB')

    @validates('lemma_palea_pubescence_pic')
    def validate_pic_eight(self, value):
        if not value:
            raise ValidationError('Lemma palea pubescence picture is required')
        if not isinstance(value, File):
            raise ValidationError('Lemma palea pubescence picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Lemma palea hair picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of lemma palea pubescence must be between 300KB and 1MB')

    @validates('grain_length_pic')
    def validate_pic_nine(self, value):
        if not value:
            raise ValidationError('Grain length picture is required')
        if not isinstance(value, File):
            raise ValidationError('Grain length picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Grain length picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of grain length must be between 300KB and 1MB')

    @validates('grain_width_pic')
    def validate_pic_ten(self, value):
        if not value:
            raise ValidationError('Grain width picture is required')
        if not isinstance(value, File):
            raise ValidationError('Grain width picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Grain width picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of grain width must be between 300KB and 1MB')

    @validates('kernel_colour_pic')
    def validate_pic_eleven(self, value):
        if not value:
            raise ValidationError('Kernel colour picture is required')
        if not isinstance(value, File):
            raise ValidationError('Kernel colour picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Kernel colour picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of kernel colour must be between 300KB and 1MB')

    @validates('kernel_length_pic')
    def validate_pic_twelve(self, value):
        if not value:
            raise ValidationError('Kernel length picture is required')
        if not isinstance(value, File):
            raise ValidationError('Kernel length picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Kernel length picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of kernel length must be between 300KB and 1MB')

    @validates('kernel_width_pic')
    def validate_pic_thirteen(self, value):
        if not value:
            raise ValidationError('Kernel width picture is required')
        if not isinstance(value, File):
            raise ValidationError('Kernel width picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Kernel width picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of kernel width must be between 300KB and 1MB')

    @validates('scent_pic')
    def validate_pic_fourteen(self, value):
        if not value:
            raise ValidationError('Scent picture is required')
        if not isinstance(value, File):
            raise ValidationError('Scent picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Scent picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture of scent must be between 300KB and 1MB')

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
    er_details = fields.Str(required=True)

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

        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Eco region image must be between 300KB and 1MB')

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

    @validates('er_details')
    def validate_ec_details(self, value):
        if not value:
            raise ValidationError('Eco region details is required')
        # if not re.match(r'^\s*(\w+\s+){20,30}$', value):
        #     raise ValidationError('Eco region details must be between 20 and 30 words')
        word_count = len(re.findall(r'\b\w+\b', value))
        if word_count < 20 or word_count > 30:
            raise ValidationError('Eco region details must be between 20 and 30 words')


class CulinaryUpload(Schema):
    g_v_id = fields.Str(required=True)
    culinary = fields.Raw(required=True)
    pic_one = fields.Raw(required=True)
    pic_two = fields.Raw(required=False)
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

    @validates('culinary')
    def validate_recipe(self, value):
        if not value:
            raise ValidationError('Culinary is required')

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

        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Picture one must be between 300KB and 1MB')

    @validates('pic_two')
    def validate_pic_two(self, value):
        if value:
            if not isinstance(value, File):
                raise ValidationError('Picture two must be a file')
            if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                raise ValidationError('Picture two must be a JPEG, JPG or PNG file')
            value.seek(0, 2)  # Seek to the end of the file
            file_size = value.tell()  # Get the current position (i.e., the file size)
            value.seek(0)  # Seek back to the beginning of the file

            if not (300 * 1024 <= file_size <= 1024 * 1024):
                raise ValidationError('Picture two must be between 300KB and 1MB')

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
    day_of_seed_sowing = fields.Str(required=True)
    field_preparation_weeding = fields.Str(required=True)
    transplantation = fields.Str(required=True)
    tillering_starts = fields.Str(required=True)
    flowering = fields.Str(required=True)
    harvest = fields.Str(required=True)
    observed_at = fields.Str(required=True)
    day_of_seed_sowing_pic = fields.Raw(required=True)
    field_preparation_weeding_pic = fields.Raw(required=True)
    transplantation_pic = fields.Raw(required=True)
    tillering_starts_pic = fields.Raw(required=True)
    flowering_pic = fields.Raw(required=True)
    harvest_pic = fields.Raw(required=True)
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

    @validates('day_of_seed_sowing')
    def validate_day_of_seed_sowing(self, value):
        if not value:
            raise ValidationError('Day of seed sowing is required')

        if not value.isdigit():
            raise ValidationError('Day of seed sowing must be a numeric value')

    @validates('field_preparation_weeding')
    def validate_field_preparation_weeding(self, value):
        if not value:
            raise ValidationError('Field preparation weeding is required')

        if not value.isdigit():
            raise ValidationError('Field preparation weeding must be a numeric value')

    @validates('transplantation')
    def validate_transplantation(self, value):
        if not value:
            raise ValidationError('Transplantation is required')

        if not value.isdigit():
            raise ValidationError('Transplantation must be a numeric value')

    @validates('tillering_starts')
    def validate_tillering_starts(self, value):
        if not value:
            raise ValidationError('Tillering starts is required')

        if not value.isdigit():
            raise ValidationError('Tillering starts must be a numeric value')

    @validates('flowering')
    def validate_flowering(self, value):
        if not value:
            raise ValidationError('Flowering is required')

        if not value.isdigit():
            raise ValidationError('Flowering must be a numeric value')

    @validates('harvest')
    def validate_harvest(self, value):
        if not value:
            raise ValidationError('Harvest is required')

        if not value.isdigit():
            raise ValidationError('Harvest must be a numeric value')

    @validates('observed_at')
    def validate_observed_at(self, value):
        if not value:
            raise ValidationError('Observed at is required')

        word_count = len(re.findall(r'\b\w+\b', value))
        if word_count < 30 or word_count > 50:
            raise ValidationError('Observed at must be between 30 and 50 words')

    @validates('day_of_seed_sowing_pic')
    def validate_seedbed_preparation_pic(self, value):
        if not value:
            raise ValidationError('Day of seed sowing picture is required')
        if not isinstance(value, File):
            raise ValidationError('Day of seed sowing picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Day of seed sowing picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Day of seed sowing picture must be between 300KB and 1MB')

    @validates('field_preparation_weeding_pic')
    def validate_field_preparation_weeding_pic(self, value):
        if not value:
            raise ValidationError('Field preparation weeding picture is required')
        if not isinstance(value, File):
            raise ValidationError('Field preparation weeding picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Field preparation weeding picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Field preparation weeding picture must be between 300KB and 1MB')

    @validates('transplantation_pic')
    def validate_transplantation_pic(self, value):
        if not value:
            raise ValidationError('Transplantation picture is required')
        if not isinstance(value, File):
            raise ValidationError('Transplantation picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Transplantation picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Transplantation picture must be between 300KB and 1MB')

    @validates('tillering_starts_pic')
    def validate_tillering_starts_pic(self, value):
        if not value:
            raise ValidationError('Tillering starts picture is required')
        if not isinstance(value, File):
            raise ValidationError('Tillering starts picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Tillering starts picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Tillering starts picture must be between 300KB and 1MB')

    @validates('flowering_pic')
    def validate_flowering_pic(self, value):
        if not value:
            raise ValidationError('Flowering picture is required')
        if not isinstance(value, File):
            raise ValidationError('Flowering picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Flowering picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Flowering picture must be between 300KB and 1MB')

    @validates('harvest_pic')
    def validate_harvest_pic(self, value):
        if not value:
            raise ValidationError('Harvest picture is required')
        if not isinstance(value, File):
            raise ValidationError('Harvest picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Harvest picture must be a JPEG, JPG or PNG file')
        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file
        if not (300 * 1024 <= file_size <= 1024 * 1024):
            raise ValidationError('Harvest picture must be between 300KB and 1MB')

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
