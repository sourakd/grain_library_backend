import re

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from werkzeug.datastructures import FileStorage as File

from db_connection import database_connect_mongo

ALPHABET_ERROR_MESSAGE = "Please enter alphabet only for name field"
name_check = "^[a-zA-Z\s]*\S$"
password_check = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


class GrainRegistrationSchema(Schema):
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    grain = fields.Str(required=True)
    grain_pic = fields.Raw(required=True)

    @validates('grain')
    def validate_grain(self, value):
        db = database_connect_mongo()
        db1 = db["grain"]
        if db1.count_documents({"grain": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError({"message": {"grain": ["This grain is already added"]}})

        if not re.match(name_check, value):
            raise ValidationError({"message": {"grain": [ALPHABET_ERROR_MESSAGE]}})

    @validates('grain_pic')
    def validate_grain_pic(self, value):
        if not value:
            raise ValidationError('Picture is required')
        if not isinstance(value, File):
            raise ValidationError('Picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Picture must be a JPEG, JPG or PNG file')

        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if not (300 * 1024 <= file_size <= 500 * 1024):
            raise ValidationError('Picture must be between 300KB and 1MB')


class GrainVariantRegistrationSchema(Schema):
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    grain = fields.Str(required=True)
    grain_variant = fields.Str(required=True)

    @validates_schema()
    def validate_grain_variant(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["grain"]
        if db1.count_documents({"grain": data['grain'], "grain_variant": data['grain_variant']}):
            raise ValidationError({"grain_variant": ["This variant already added under this grain"]})

        if not re.match(name_check, data["grain_variant"]):
            raise ValidationError({"grain_variant": [ALPHABET_ERROR_MESSAGE]})


grain_registration_schema = GrainRegistrationSchema()
grain_variant_registration_schema = GrainVariantRegistrationSchema()
