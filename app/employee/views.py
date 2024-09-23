import datetime as dt
from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from flask_cors import cross_origin
from passlib.hash import pbkdf2_sha256
from db_connection import database_connect_mongo
from employee_helpers import EmployeeSchema
from marshmallow.exceptions import ValidationError

employee = Blueprint('employee', __name__)


class employee_registration(MethodView):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            db = database_connect_mongo()
            db1 = db["employee_registration"]
            data = request.get_json()
            employee_name = data["employee_name"]
            email_id = data["email_id"].lower()
            password = data["password"]
            type_id = data["type_id"]

            if employee_name and email_id and password and type_id:

                emp_schema = EmployeeSchema()

                data = {"status": "active", "type_id": type_id,
                        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": None,
                        "password": password, "employee_name": employee_name, "email_id": email_id}

                # Validate the data using the schema
                try:
                    validated_data = emp_schema.load(data)
                except ValidationError as err:
                    response = {"message": err.messages, "status": "val_error"}
                    return make_response(jsonify(response)), 200

                else:
                    # Hash the password
                    validated_data["password"] = pbkdf2_sha256.hash(validated_data["password"])

                    # Update the updated_at field
                    validated_data["created_at"] = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    # Insert the data into the database
                    db1.insert_one(validated_data)

                    # Remove the password from the data
                    del validated_data["password"]

                    # Extract the _id value
                    validated_data["_id"] = str(validated_data["_id"])

                    # Create the response
                    response = {"message": "Employee registration successful", "status": "success",
                                "data": validated_data}

                    # Return the response
                    return make_response(jsonify(response)), 200

            else:
                response = {"status": 'val_error', "message": "Please enter all details"}
                return make_response(jsonify(response)), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": 'val_error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200


emp_reg = employee_registration.as_view('emp_reg_view')
employee.add_url_rule('/employee/registration', view_func=emp_reg, methods=['POST'])
