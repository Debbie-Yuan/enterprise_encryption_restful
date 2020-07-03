from App.Apis.User import client_api


def init_apis(app):
    client_api.init_app(app)
