from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from settings.configuration import app_config

mdb = MongoEngine()
bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config['DEBUG'] = {
        'title': 'Grain Library',
        'description': "Learning Software App"
                       "\n This is the registry API for Learning Software App. It allows you to access, manage, "
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

    return app
