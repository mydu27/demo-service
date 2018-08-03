from datetime import datetime

import mongoengine

from deemo.model.base_model import BaseModel

# mongoengine.connect('holoread', alias='holoread', host=settings.MONGO_HOST)


class User(BaseModel, mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    password = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    added = mongoengine.DateTimeField(required=True, default=datetime.now)
    email = mongoengine.EmailField(required=True, unique=True)
    level = mongoengine.IntField(required=True, default=1)

    meta = {'indexes': ['username', 'email', 'added'],
            'collection': 'users'}

    @classmethod
    def validate_password(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.password.encode('utf-8') == password.encode('utf-8'):
            return user

    @classmethod
    def get_by_username(cls, username):
        return cls.objects(username=username).first()

    @property
    def is_admin(self):
        return self.level == 9

    @property
    def is_editor(self):
        return self.level == 2

    def api_base_response(self):
        return {'id': str(self.id), 'name': self.name}

    def me(self):
        return self.api_response()

    def api_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'name': self.name,
            'email': self.email if self.email else ''
        }


def authenticate(user, username, password):
    user = User.validate_password(username, password)
    return user if user else None


def identity(payload):
    return User.objects.get(id=payload['identity'])
