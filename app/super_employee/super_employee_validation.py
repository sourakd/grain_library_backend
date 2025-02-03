from marshmallow import Schema, fields, ValidationError, validates_schema
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from db_connection import database_connect_mongo

ALPHABET_ERROR_MESSAGE = "Please enter alphabet only for name field"
name_check = "^[a-zA-Z\s]*\S$"
password_check = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


class SuperEmployeeLoginSchema(Schema):
    email_id = fields.Email(required=True)
    password = fields.Str(required=True)

    @validates_schema
    def validate_login(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["super_location"]
        location = db1.find_one({"email_id": {"$eq": data['email_id']}}, collation={"locale": "en", "strength": 2})

        if location is not None:
            if not pbkdf2_sha256.verify(data['password'], location['password']):
                raise ValidationError("Incorrect password")

        else:
            raise ValidationError({"email_id": ["Email does not exist"]})


super_employee_login_schema = SuperEmployeeLoginSchema()
