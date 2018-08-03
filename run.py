#
# holoread
# run
#
# Created by yangxiaotong on 19/6/2018.
# 13:26
# Copyright (c) 2018 Geekpark. All rights reserved.
#

from flask_apidoc import ApiDoc
from flask_apidoc.commands import GenerateApiDoc
from flask_script import Manager

import mongoengine
# from threading import Timer
# from apscheduler.schedulers.background import BackgroundScheduler

from deemo import api, app, settings
from deemo.api import v1


mongoengine.connect('deemo', host=settings.MONGO_HOST)


ApiDoc(app=app, url_path='/api/docs', dynamic_url=False)

manager = Manager(app)
manager.add_command('apidoc', GenerateApiDoc())


# sched = BackgroundScheduler()


# sched.start()

if __name__ == '__main__':
    manager.run()
