import hashlib
import json

import os
import mongoengine

# from deemo import settings
# from deemo.common.logging import logger


def is_english(word):
    try:
        word.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def mail_generator(template: str, format_map: dict) -> str:
    return template.format_map(format_map)


def map_reduce(cls: mongoengine.Document, query: dict,
               map_f: str, reduce_f: str):
    if isinstance(cls(), mongoengine.Document):
        return cls.objects(**query).map_reduce(map_f, reduce_f, "inline")
    else:
        raise 'Class is not extend mongoengine.Document'


def convert_list(list_):
    """处理_id."""
    for item in list_:
        item['id'] = item['_id']['$oid']
        item.pop('_id', None)
    return list_


def paging(cls=None, field=None, page=None, page_size=None, order_by=None,
           query=None):
    """
    分页函数 支持按照字段分页

    @param cls: 分页的model
    @type: mongoengine.Document
    @param field: 需要分页的字段名
    @type field: str
    @param query: 查询语句
    @type query: dict
    @param page: 当前页面
    @type page: int
    @param page_size: 每页条数
    @type page_size: int
    @param order_by: 排序语句 如: ['-added','-name']
    @type order_by: list of str
    @return: 分页结果
    @rtype: dict
    """
    if query is None:
        query = {}
    if page is None:
        page = 1
    if page_size is None:
        page_size = 10
    if order_by is None:
        order_by = []
    if not isinstance(cls(), mongoengine.Document):
        raise 'Class is not extend mongoengine.Document'

    def get_limit(count, page, page_size):
        if page <= 0:
            page = 1
        page_sum = int((count - 1) / page_size + 1)
        start = (page - 1) * page_size
        has_previous = True if page > 1 else False
        has_next = True if page < page_sum else False
        return {'start': start, 'page_sum': page_sum,
                'has_next': has_next, 'has_previous': has_previous,
                'count': count}

    if field:
        pipeline = [{'$project': {'count': {'$size': '$' + field}}}]
        count = list(cls.objects(**query).aggregate(*pipeline))[0]['count']
        results = get_limit(count, page, page_size)
        fields_query = {f'slice__{field}': [results['start'], page_size]}
        list_ = cls.objects(**query).fields(**fields_query).order_by(*order_by)
        results['list'] = list_[0][field]
    else:
        count = cls.objects(**query).count()
        results = get_limit(count, page, page_size)
        qery_set = cls.objects(**query).order_by(*order_by)
        list_ = qery_set.skip(results['start']).limit(page_size)
        # results['list'] = json.loads(list_.to_json())
        results['list'] = list(map(lambda a: a.api_base_response(), list_))

    results['current_page'] = page
    results.pop('start', None)
    return results


def api_response(data=None, status_code=200):
    if data is None:
        data = {}
    return {'data': data}, status_code, {'Access-Control-Allow-Origin': '*'}


def api_error_response(msg, status_code=500):
    return {'msg': msg}, status_code, {'Access-Control-Allow-Origin': '*'}


def md5(text):
    h = hashlib.md5()
    h.update(text.encode())
    return h.hexdigest()


def item_pop(item, pop_list):
    [item.pop(name, None) for name in pop_list]
    return item


def convert_oid(item: dict, field_name: str):
    item[field_name] = item[field_name]['$oid']
    return item


def convert_id(item: dict) -> dict:
    item['id'] = item['_id']['$oid']
    item.pop('_id')
    return item


def convert_dict_key(item: dict, covert: dict) -> dict:
    for key, value in covert.items():
        item[key] = item.pop(value)
    return item


def to_fixed_4(item):
    """
    保留四位小数点
    """
    return f'{float(item):10.4f}'


def open_group_file():
    file_path = os.getcwd() + '/crm/common/group.json'
    with open(file_path, 'r', encoding='UTF-8') as f:
        group_data = json.load(f)
    return group_data


def parse_HTML(file):
    return ''.join([line.rstrip('\n') for line in file.readlines()])
