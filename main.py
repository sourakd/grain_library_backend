from app import create_app

app = [create_app(config_name='development'), create_app(config_name='production')]
used_app = app[0]

if __name__ == '__main__':
    used_app.run(host="127.0.0.1", port=8000, debug=True)
