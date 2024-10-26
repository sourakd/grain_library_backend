from functools import wraps
import jwt
from flask import jsonify, request, current_app
from db_connection import database_connect_mongo
from datetime import datetime


def Admin_Access(U):
    """
    Decorator to check if the user has admin access based on the token in the request headers.
    """

    @wraps(U)
    def wrapper(*args, **kwargs):
        # Get the token from the request headers
        token = request.headers.get('token')

        # Check if the token is valid and not expired
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])

        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token", "status": "val_error"}), 401

        # Connect to the MongoDB database
        db = database_connect_mongo()
        db1 = db["jwt"]

        # Check if the token is active in the database
        if db1.find_one({"token": token, "status": "active"}):
            # Check if the user has admin role
            if decoded_token.get("role_id") == '1':
                # If admin, call the original function
                return U(*args, **kwargs)
            else:
                # If not admin, return an error response
                return jsonify({"message": "unauthorized access", "status": "val_error"}), 401
        else:
            # If the token is not active, return an error response
            return jsonify({"message": "Token is not active", "status": "val_error"}), 401

    return wrapper
