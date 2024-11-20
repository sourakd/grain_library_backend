from marshmallow import Schema, fields, validates, ValidationError, validates_schema
import re
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import request
from db_connection import database_connect_mongo


class EmployeeRegistrationSchema(Schema):
    status = fields.Str(required=True)
    type_id = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    password = fields.Str(required=True)
    employee_name = fields.Str(required=True)
    email_id = fields.Email(required=True)

    @validates('password')
    def validate_password(self, value):
        pachk = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        if not re.match(pachk, value):
            raise ValidationError(
                "Please enter Minimum eight characters, at least one letter, one number and one special character for "
                "password field")

    @validates('employee_name')
    def validate_employee_name(self, value):
        nchk = "^[a-zA-Z\s]*\S$"
        if not re.match(nchk, value):
            raise ValidationError("Please enter alphabet only for name field")

    @validates('email_id')
    def validate_email_id(self, value):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$regex": re.escape(value), "$options": "i"}}) > 0:
            raise ValidationError("Email already exists")


class EmployeeLoginSchema(Schema):
    email_id = fields.Email(required=True)
    password = fields.Str(required=True)

    @validates_schema
    def validate_login(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": data['email_id']}}, collation={"locale": "en", "strength": 2}) == 1:

            employee = db1.find_one({"email_id": {"$regex": re.escape(data['email_id']), "$options": "i"}})
            if not pbkdf2_sha256.verify(data['password'], employee['password']):
                raise ValidationError("Incorrect password")

        else:
            raise ValidationError("Email does not exist")


employee_registration_schema = EmployeeRegistrationSchema()
employee_login_schema = EmployeeLoginSchema()
