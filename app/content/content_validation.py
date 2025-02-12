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

    @validates('story')
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


StoryUploadSchema = StoryUpload()
