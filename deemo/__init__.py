#
# holoread
# __init__.py
#
# Created by yangxiaotong on 19/6/2018.
# 14:00
# Copyright (c) 2018 Geekpark. All rights reserved.
#

import datetime
import types

from flask import Flask
from flask_jwt import JWT
from deemo.api.base import Service
from deemo.model.user import authenticate, identity

from deemo.common import util

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_AUTH_URL_RULE'] = None
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=60)
# app.config['JWT_AUTH_URL_OPTIONS'] = {'methods': ['POST', 'OPTIONS']}
jwt = JWT(app, authenticate, identity)


@jwt.jwt_payload_handler
def jwt_payload_handler(identity):
    iat = datetime.datetime.utcnow()
    exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
    identity = getattr(identity, 'id', None) or identity['id']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': str(identity)}


@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    data = {'access_token': access_token.decode('utf-8')}
    return rest_api.make_response(*util.api_response(data=data))


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


rest_api = Service(app)

rest_api.route = types.MethodType(api_route, rest_api)
