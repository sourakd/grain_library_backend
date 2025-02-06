import re

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from db_connection import database_connect_mongo

ALPHABET_ERROR_MESSAGE = "Please enter alphabet only for name field"
name_check = "^[a-zA-Z\s]*\S$"
password_check = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


class CountryRegistrationSchema(Schema):
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    password = fields.Str(required=True)
    location = fields.Str(required=True)
    email_id = fields.Email(required=True)
    emp_assign = fields.Str(required=True)

    @validates('location')
    def validate_location(self, value):
        db = database_connect_mongo()
        db1 = db["location"]
        if db1.count_documents({"location": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("This country already added")

        if not re.match(name_check, value):
            raise ValidationError(ALPHABET_ERROR_MESSAGE)

    @validates('password')
    def validate_password(self, value):
        if not re.match(password_check, value):
            raise ValidationError("Please enter Minimum eight characters, at least one letter, one number and one "
                                  "special character for password field")

    @validates('email_id')
    def validate_email_id(self, value):
        db = database_connect_mongo()
        db1 = db["location"]
        db2 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("Email already exists")
        if db2.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("An employee with this email already exists")


class RegionRegistrationSchema(Schema):
    status = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    password = fields.Str(required=True)
    country = fields.Str(required=True)
    location = fields.Str(required=True)
    email_id = fields.Email(required=True)
    emp_assign = fields.Str(required=True)

    @validates_schema
    def validate_region(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["location"]
        if db1.count_documents({"country": data['country'], "location": data['location']}):
            raise ValidationError({"region": ["This region already added under this country"]})

        if not re.match(name_check, data['location']):
            raise ValidationError(ALPHABET_ERROR_MESSAGE)

    @validates('email_id')
    def validate_email_id(self, value):
        db = database_connect_mongo()
        db1 = db["location"]
        db2 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("Email already exists")
        if db2.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("An employee with this email already exists")

    @validates('password')
    def validate_password(self, value):
        if not re.match(password_check, value):
            raise ValidationError(
                "Please enter Minimum eight characters, at least one letter, one number and one special character for "
                "password field")

    @validates('country')
    def validate_country(self, value):
        db = database_connect_mongo()
        db1 = db["location"]
        if db1.count_documents({"location": {"$eq": value}, "type_id": "country"},
                               collation={"locale": "en", "strength": 2}) == 0:
            raise ValidationError("Country not found")


class LoginSchema(Schema):
    email_id = fields.Email(required=True)
    password = fields.Str(required=True)

    @validates_schema
    def validate_login(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["location"]
        location = db1.find_one({"email_id": {"$eq": data['email_id']}}, collation={"locale": "en", "strength": 2})

        if location is not None:

            if location['emp_assign'] == "false":
                raise ValidationError({"assign": ["This location is not assigned to any employee"]})

            if not pbkdf2_sha256.verify(data['password'], location['password']):
                raise ValidationError({"password": ["Password is incorrect"]})

        else:
            raise ValidationError({"email_id": ["Email does not exist"]})


country_registration_schema = CountryRegistrationSchema()
region_registration_schema = RegionRegistrationSchema()
login_schema = LoginSchema()
