from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mongoengine import MongoEngine

from settings.configuration import app_config

mdb = MongoEngine()
bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config['DEBUG'] = {
        'title': 'Grain Library',
        'description': "Learning Software App"
                       "\n This is the registry API for Grain Library App. It allows you to access, manage, "
                       "and update API's.\n"
                       "\nAuthor: Sourav Kumar Dhar "
                       "\nCompany: Symagine Pvt. Ltd.\n",
        'contact': {
            'Developer1': 'Sourav Dhar ',
            'Developer2': 'Rimi Das',
            'Company': 'Symagine Pvt. Ltd.',
        },

        'schemes': [
            'https'
        ],

        'license': {
            'name': 'private'
        },

        'specs_route': '/apidocs/'
    }
    mdb.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    from app.employee_access.views import employee_access
    from app.location.views import location_add
    from app.grain.views import grain_add
    from app.super_employee.views import super_employee_access
    from app.content.views import content_blueprint
    from app.user.views import user

    app.register_blueprint(employee_access)
    app.register_blueprint(location_add)
    app.register_blueprint(grain_add)
    app.register_blueprint(super_employee_access)
    app.register_blueprint(content_blueprint)
    app.register_blueprint(user)
    return app
