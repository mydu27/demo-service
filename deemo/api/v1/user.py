
from flask import request

from flask_restful import reqparse
from flask_jwt import JWTError
from flask_jwt import jwt_required

from deemo import rest_api
from deemo import app, jwt
from deemo.api.base import BaseAPI
from deemo.common import util
from deemo.model.user import User
from deemo.service.user import get_current_user, rule_required


@rest_api.route('/api/v1/login', endpoint='login')
class LoginAPI(BaseAPI):
    def post(self):
        """
        @api {post} /v1/login 登录
        @apiName login
        @apiGroup login
        @apiDescription 进行操作之前需要登录
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username":"admin",
            "password":"123456"
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "File not found"
            }
        """
        data = request.get_json()
        username = data.get(app.config.get('JWT_AUTH_USERNAME_KEY'), None)
        password = data.get(app.config.get('JWT_AUTH_PASSWORD_KEY'), None)
        criterion = [username, password, len(data) == 2]
        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')

        identity = jwt.authentication_callback(
            User, username, util.md5(password))
        if identity:
            access_token = jwt.jwt_encode_callback(identity)
            return jwt.auth_response_callback(access_token, identity)
        else:
            raise JWTError('Bad Request', 'Invalid credentials')


@rest_api.route('/api/v1/user', endpoint='user_add')
@rest_api.route('/api/v1/user/<string:id>', endpoint='user_update')
class UserAPI(BaseAPI):
    # @jwt_required()
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('page_size', type=int, default=10)
            args = parser.parse_args()

            data = util.paging(cls=User,
                               page=args.get('page'),
                               page_size=args.get('page_size'))
            return util.api_response(data=data)
        user = User.get_by_id(id=id)
        return util.api_response(data=self.me(user))

    def me(self, user):
        return user.api_response()

    @jwt_required()
    @rule_required([9])
    def post(self):
        """
        @api {post} /v1/user 添加用户
        @apiName user
        @apiGroup user
        @apiDescription 添加用户
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username":"admin",
            "password":"123456",
            "email":"admin@geekpark.net"
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "File not found"
            }
        """
        data = request.get_json()
        username = data['username'].strip().lower()
        password = data['password'].strip()
        name = data['name'].strip()
        email = data['email']
        level = data['level']

        if not (username and password and email):
            raise ValueError('请把所有数据填写完整。')

        if User.get_by_username(username):
            raise ValueError('该用户已存在')

        user = User(
            username=username,
            password=util.md5(password),
            name=name,
            email=email,
            level=level)
        user.save()
        return util.api_response(data=self.me(user))

    @jwt_required()
    def put(self, id=None):
        """
        @api {put} /v1/user 修改用户
        @apiName user
        @apiGroup user
        @apiDescription 修改用户，用户名不能修改
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username":"admin",
            "password":"123456",
            "email":"admin@geekpark.net"
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "File not found"
            }
        """
        if id is None:
            raise ValueError('Id not found')
        data = request.get_json()
        current_user = get_current_user()
        user = User.objects.get(id=id)
        if 'username' in data and user.username != data['username']:
            return util.api_response(
                data={'msg': 'Can\'t modify username'}, status_code=403
            )
        if str(current_user.id) == str(user.id):
            if 'level' in data:
                del data['level']
        else:
            if not current_user.is_admin:
                return util.api_response(
                    data={'msg': 'Don\'t have authority'}, status_code=403)
        if 'password' in data:
            data['password'] = util.md5(data['password'])
        user.update(**data)
        user.reload()
        return util.api_response(data=self.me(user))

    @jwt_required()
    @rule_required([9])
    def delete(self, id=None):
        """
        @api {delete} /v1/user 删除用户
        @apiName user
        @apiGroup user
        @apiDescription 删除用户，仅超级管理员9权限可操作
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username":"admin",
            "password":"123456",
            "email":"admin@geekpark.net"
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "File not found"
            }
        """
        if id is None:
            raise ValueError('Id not found')
        user = User.get_by_id(id=id)
        user.delete()
        return util.api_response(data={'msg': 'Success Delete'})
