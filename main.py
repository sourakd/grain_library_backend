from app import create_app

used_app = create_app(config_name='production')

if __name__ == '__main__':
    used_app.run(host="127.0.0.1", port=8000)

# if __name__ == '__main__':
#     waitress.serve(app, host="127.0.0.1", port=8000)

# if __name__ == '__main__':
#     used_app.run(host="grain.learn-up.org", port=8000)
