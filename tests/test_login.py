from nose import tools
from tests import test_app, user_data
from deemo.model import User
from deemo.common import util
from copy import deepcopy
import mongoengine
import json


class TestUser():
    def setUp(self):
        # 测试数据
        self.test_data = deepcopy(user_data)
        self.__test_save()
        self.__test_login()

    def tearDown(self):
        temp = User.objects(username='caihaoyu').first()
        if temp:
            temp.delete()

    def __test_save(self):
        user = User(**self.test_data)
        user.password = util.md5(user.password)
        user.email = 'email'

        with tools.assert_raises(mongoengine.errors.ValidationError):
            user = user.save()

        tools.assert_is_none(user.id)

        user = User(**self.test_data)
        user.password = util.md5(user.password)
        user.save()
        tools.assert_is_not_none(user.id)
        self.id = str(user.id)
        self.username = user.username
        self.password = 'test'

    def __test_login(self):
        test_user = {'username': self.username,
                     'password': self.password}
        test_user['password'] = self.password + '222'
        data = json.dumps(test_user)
        response = test_app.post('/api/v1/login',
                                 data=data,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 401)

        test_user['password'] = self.password
        data = json.dumps(test_user)
        response = test_app.post('/api/v1/login',
                                 data=data,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 200)
        json_resp = json.loads(response.data)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('access_token'))
        self.token = f'JWT {json_resp["data"]["access_token"]}'

    @tools.nottest
    def test_paging(self, response, page, page_size=10):
        """
        翻页功能测试
        @param page: 页数
        @type page: int
        @param page_size: 每页条数
        @type page_size: int
        @return: None
        @rtype: None
        """
        tools.assert_equals(response.status_code, 200)
        json_resp = json.loads(response.data)
        user = User.objects()
        length = len(user)
        list_len = page_size

        tools.assert_equals(json_resp['data']['page_sum'], length//10+1)
        if page == json_resp['data']['page_sum']:
            list_len = length % page_size
            if list_len == 0:
                list_len = 10

        tools.assert_equals(len(json_resp['data']['list']), list_len)

        tools.assert_equals(json_resp['data']['count'], length)
        tools.assert_equals(json_resp['data']['current_page'], page)

    def test_get_all(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'cccddd'
        t_data['email'] = '1256@geekpark.net'
        t_data['password'] = 'test1234'
        t_data['name'] = 'aaa'
        data = json.dumps(t_data)

        response = test_app.get('/api/v1/user',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        self.test_paging(response, 1)

        t_user = User(**t_data)
        t_user.save()
        response = test_app.get('/api/v1/user',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_equals(json_resp['data']['count'], 3)

    def test_get(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'ccc'
        t_data['email'] = '123456@geekpark.net'
        t_data['password'] = 'test1234'
        t_data['name'] = 'aaa'
        t_user = User(**t_data)
        data = json.dumps(t_data)

        response = test_app.get(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': "Id is not found."})

        t_user.save()
        response = test_app.get(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))

    def test_post(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = self.token
        t_data['email'] = 'yangxiaotong@geekpark.net'
        data = json.dumps(t_data)
        response = test_app.post('/api/v1/user',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': "user don't has authority"})

        user = User.get_by_id(self.id)
        user.level = 9
        user.save()
        response = test_app.post('/api/v1/user',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))

    def test_put(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'bbb'
        t_data['email'] = 'yangxiao@geekpark.net'
        t_data['password'] = 'test1'
        t_data['name'] = 'aaa'
        t_user = User(**t_data)
        t_user.save()
        data = json.dumps(t_data)

        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        tools.assert_equals(response.status_code, 403)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Don\'t have authority'})
        user = User.get_by_id(self.id)
        user.level = 9
        user.save()

        t_data['username'] = 'ccc'
        data = json.dumps(t_data)
        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        tools.assert_equals(response.status_code, 403)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Can\'t modify username'})

        t_data['password'] = 'test2'
        t_data['username'] = 'bbb'
        data = json.dumps(t_data)
        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        self.username = t_data.get('username')
        self.password = t_data.get('password')
        self.__test_login()

    def test_delete(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'ccc'
        t_data['email'] = '123456@geekpark.net'
        t_data['password'] = 'test1234'
        t_data['name'] = 'aaa'
        t_user = User(**t_data)
        t_user.save()
        data = json.dumps(t_data)

        response = test_app.delete(f'/api/v1/user/{str(t_user.id)}',
                                   data=data,
                                   headers=headers,
                                   content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': "user don't has authority"})

        user = User.get_by_id(self.id)
        user.level = 9
        user.save()
        response = test_app.delete(f'/api/v1/user/{str(t_user.id)}',
                                   data=data,
                                   headers=headers,
                                   content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
