from marshmallow import Schema, fields, validates, ValidationError
import re
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import request


class LoginSchema(Schema):
    email_id = fields.Email(required=True)
    password = fields.Str(required=True)

    @validates('email_id')
    def validate_email_id(self, value):
        from db_connection import database_connect_mongo
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) == 0:
            raise ValidationError("Email does not exists")

    @validates('password')
    def validate_password(self, value):
        from db_connection import database_connect_mongo
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) == 1:
            employee = db1.find_one({"email_id": {"$regex": re.escape(request.json['email_id']), "$options": "i"}})
            if not pbkdf2_sha256.verify(value, employee['password']):
                raise ValidationError("Incorrect password")


login_schema = LoginSchema()
