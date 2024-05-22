from app import create_app

app = [create_app(config_name='development'), create_app(config_name='production')]

if __name__ == '__main__':
    # Check if the host is localhost
    app[0].run(host="127.0.0.1", port=8000, debug=True)
