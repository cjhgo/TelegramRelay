#coding: utf-8
#created at 17-3-7 18:19

import datetime
import logging
from tornado import gen
from ..service import Service, register_service


@register_service
class BlogService(Service):
    name = "blog"
    collection_name = "blog"

    @gen.coroutine
    def handler(self, body_list, message_id):
        message_id, submessage_id = Service.get_message_id(message_id)
        logging.debug(message_id)
        logging.debug(submessage_id)
        items = body_list.split('\n')
        url = items.pop(0)
        meta = {}
        for _ in items:
            key, value = _.split(': ', 1)
            meta[key] = value
        meta["message_id"] = message_id
        meta["submessage_id"] = submessage_id
        meta["url"] = url
        meta["crts"] = datetime.datetime.utcnow()
        yield self.db[self.collection_name].update(
            {
                "message_id": message_id,
                "submessage_id": submessage_id,
            },
            {
                "$set": meta
            },
            upsert=True)
