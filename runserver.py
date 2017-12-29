# encoding:utf8
# from wuaiwow import create_app
from celery_worker import app

# set up the flask app
# app = create_app()


def main():

    app.run(debug=app.debug, port=5001, host='0.0.0.0')

if __name__ == "__main__":
    main()
