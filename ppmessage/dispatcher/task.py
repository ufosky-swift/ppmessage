# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 .
# Guijin Ding, dingguijin@gmail.com
#
#

from .policy import BroadcastPolicy

from ppmessage.db.models import AppInfo
from ppmessage.db.models import DeviceUser
from ppmessage.db.models import ConversationInfo
from ppmessage.db.models import MessagePushTask

from ppmessage.core.constant import YVOBJECT
from ppmessage.core.redis import redis_hash_to_dict

import logging
import json

class TaskHandler():

    def __init__(self, _app):
        self.application = _app

    def _dispatch(self):
        logging.info("DISPATCH: type:%s, subtype:%s, body:%s, ft:%s, tt:%s" % (self._task["message_type"], self._task["message_subtype"], self._task["body"], self._task["from_type"], self._task["to_type"]))
        _cls = BroadcastPolicy
        _obj = _cls(self)
        _obj.dispatch()
        return

    def _prepare(self, _task_uuid):
        if not _task_uuid:
            logging.error("Can't find task for task uuid: %s" % (_data["task_uuid"]))
            return None
        
        _redis = self.application.redis
        _task = redis_hash_to_dict(_redis, MessagePushTask, _task_uuid)
        if _task == None:
            logging.error("Can't find task for task uuid: %s" % (_data["task_uuid"]))
            return None
        
        _user = None
        if _task.get("from_type") == YVOBJECT.DU:
            _user = redis_hash_to_dict(_redis, DeviceUser, _task.get("from_uuid"))
            if _user != None:
                del _user["user_password"]

        # conversation maybe None for explicit message SYS LOGOUT
        _conversation = redis_hash_to_dict(_redis, ConversationInfo, _task.get("conversation_uuid"))

        _task["_user"] = _user
        _task["_conversation"] = _conversation
        
        self._task = _task
        return self._task
                                           
    def task(self, _data):
        if not self._prepare(_data.get("task_uuid")):
            return
        self._dispatch()
        return

