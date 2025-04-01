import re

from marshmallow import Schema, fields, validates, ValidationError, validates_schema

from db_connection import database_connect_mongo

ALPHABET_ERROR_MESSAGE = "Please enter alphabet only for name field"
name_check = "^[a-zA-Z\s]*\S$"
password_check = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


class GrainRegistrationSchema(Schema):
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    grain = fields.Str(required=True)

    @validates('grain')
    def validate_grain(self, value):
        db = database_connect_mongo()
        db1 = db["grain"]
        if db1.count_documents({"grain": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError({"message": {"grain": ["This grain is already added"]}})

        if not re.match(name_check, value):
            raise ValidationError({"message": {"grain": [ALPHABET_ERROR_MESSAGE]}})


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
