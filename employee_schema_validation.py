from marshmallow import Schema, fields, validates, ValidationError
import re
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import request


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
        from db_connection import database_connect_mongo
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$regex": re.escape(value), "$options": "i"}}) > 0:
            raise ValidationError("Email already exists")


class EmployeeLoginSchema(Schema):
    email_id = fields.Email(required=True)
    password = fields.Str(required=True)
    @validates('email_id')
    def validate_email_id(self, value):
        from db_connection import database_connect_mongo
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$regex": re.escape(value), "$options": "i", "status": "active"}}) == 0:
            raise ValidationError("Email does not exists")

    @validates('password')
    def validate_password(self, value):
        from db_connection import database_connect_mongo
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$regex": re.escape(value), "$options": "i", "status": "active"}}) == 1:
            employee = db1.find_one({"email_id": {"$regex": re.escape(value), "$options": "i"}})
            if not pbkdf2_sha256.verify(request.json['password'], employee['password']):
                raise ValidationError("Incorrect password")


employee_registration_schema = EmployeeRegistrationSchema()
employee_login_schema = EmployeeLoginSchema()
