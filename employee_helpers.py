from marshmallow import Schema, fields, validates, ValidationError
import re


class EmployeeSchema(Schema):
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
