import re

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from werkzeug.datastructures import FileStorage as File

from db_connection import database_connect_mongo

name_check = re.compile(r"^[a-zA-Z\s]*\S$")
phone_pattern = re.compile(r'^\d{10}$')


class EmployeeRegistrationSchema(Schema):
    status = fields.Str(required=True)
    type_id = fields.Str(required=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    employee_name = fields.Str(required=True)
    email_id = fields.Email(required=True)
    profile_pic = fields.Raw(required=True)
    phone_number = fields.Str(required=True)
    address = fields.Str(required=True)
    id_proof = fields.Str(required=True)
    id_no = fields.Str(required=True)

    @validates('employee_name')
    def validate_employee_name(self, value):
        if not re.match(name_check, value):
            raise ValidationError("Please enter alphabet only for name field")

    @validates('type_id')
    def validate_type_id(self, value):
        if value not in ['admin', 'sub_admin', 'editor']:
            raise ValidationError("Please select a valid type ID. It should be either 'admin', 'sub_admin' or 'editor'")

    @validates('email_id')
    def validate_email_id(self, value):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if db1.count_documents({"email_id": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("Email already exists")

    @validates('profile_pic')
    def validate_profile_pic(self, value):
        if not value:
            raise ValidationError('Profile picture is required')
        if not isinstance(value, File):
            raise ValidationError('Profile picture must be a file')
        if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError('Profile picture must be a JPEG, JPG or PNG file')

        value.seek(0, 2)  # Seek to the end of the file
        file_size = value.tell()  # Get the current position (i.e., the file size)
        value.seek(0)  # Seek back to the beginning of the file

        if file_size > 500 * 1024:  # 500KB
            raise ValidationError('Profile picture must be less than 500KB')

        if file_size < 250 * 1024:  # 50KB
            raise ValidationError('Profile picture must be greater than 300KB')

    @validates('id_proof')
    def validate_id_proof(self, value):
        if value not in ['aadhar', 'voter']:
            raise ValidationError("Please select a valid ID proof type. It should be either 'Aadhar' or 'Voter'.")

    @validates_schema()
    def validate_id_no(self, data, **kwargs):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if data["id_proof"] == "aadhar":
            aadhar_pattern = re.compile(r'^\d{12}$')
            if not aadhar_pattern.match(data["id_no"]):
                raise ValidationError({"id_no": ["Please enter a valid Aadhar card number (12 characters)"]})
            if db1.count_documents({"id_no": {"$eq": data["id_no"]}}, collation={"locale": "en", "strength": 2}) > 0:
                raise ValidationError("Aadhar card already exists")
        elif data["id_proof"] == "voter":
            voter_pattern = re.compile(r'^[A-Z]{3}\d{7}$')
            if not voter_pattern.match(data["id_no"]):
                raise ValidationError({"id_no": ["Please enter a valid Voter ID number (10 characters)"]})
            if db1.count_documents({"id_no": {"$eq": data["id_no"]}}, collation={"locale": "en", "strength": 2}) > 0:
                raise ValidationError("Voter ID already exists")

    @validates('phone_number')
    def validate_phone_number(self, value):
        db = database_connect_mongo()
        db1 = db["employee_registration"]
        if not phone_pattern.match(value):
            raise ValidationError("Please enter a valid phone number (10 digits).")
        if db1.count_documents({"phone_number": {"$eq": value}}, collation={"locale": "en", "strength": 2}) > 0:
            raise ValidationError("Phone number already exists")


employee_registration_schema = EmployeeRegistrationSchema()
