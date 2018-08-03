import os

MONGO_HOST = os.environ.get('MONGO_HOST')
MIRROR_HOST = os.environ.get('MIRROR_HOST', 'http://data.geekpark.net')
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
HOLOREAD_HOST = os.environ.get('HOLOREAD_HOST', 'http://ng.holoread.news')
MAIL_SERVICE = os.environ.get('MAIL_SERVICE', 'http://ng.holoread.news')
TRANSLATE_FROM = os.environ.get('TRANSLATE_FROM', 'sogou')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'wuwenhan@geekpark.net')
MAIL_TAG = os.environ.get('MAIL_TAG', 'holoread-test')
MAIL_ADDRESS = os.environ.get('MAIL_ADDRESS', 'holoread-test@geekpark.net')
