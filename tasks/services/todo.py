#coding: utf-8
#created at 17-3-7 18:19

import datetime
import logging
from tornado import gen
from ..service import Service, register_service


@register_service
class TodoService(Service):
    name = "todo"
    collection_name = "todo"

    @gen.coroutine
    def handler(self, body_list, message_id):
        message_id, submessage_id = Service.get_message_id(message_id)
        logging.debug(message_id)
        logging.debug(submessage_id)

        body_list = body_list.split('\n')

        for i, _ in enumerate(body_list):
            meta = {}
            key, value = _.split(': ', 1)
            meta["task"] = value
            meta["type"] = key
            meta["message_id"] = message_id
            meta["submessage_id"] = submessage_id
            meta["task_id"] = i
            meta["crts"] = datetime.datetime.utcnow()
            yield self.db[self.db_name][self.collection_name].update(
                {
                    "message_id": message_id,
                    "submessage_id": submessage_id,
                    "task_id": i
                },
                {
                    "$set": meta
                },
                upsert=True)
