#coding: utf-8
#created at 17-3-7 18:18

import datetime
import logging
from tornado import gen
from ..service import Service, register_service


@register_service
class KeywordService(Service):
    name = "keyword"
    collection_name = "research"

    @gen.coroutine
    def handler(self, body_list, message_id):
        message_id, submessage_id = Service.get_message_id(message_id)
        logging.debug(message_id)
        logging.debug(submessage_id)
        body = [item.split('\n') for item in body_list.split('\n\n')]

        yield self.db[self.db_name][self.collection_name].update(
            {
                "message_id": message_id,
                "submessage_id": submessage_id
            },
            {
                "$set":
                    {
                        "type": "keyword",
                        "message_id": message_id,
                        "submessage_id": submessage_id,
                        "content": body[0],
                        "urls": body[1] if len(body) > 1 else [],
                        "crts": datetime.datetime.utcnow()
                    }

            },
            upsert=True)
