#coding: utf-8
#created at 17-3-7 18:18
#coding: utf-8
#created at 17-3-7 18:18

import datetime
import logging
from tornado import gen
from ..service import Service, register_service


@register_service
class ToreadlinkService(Service):
    name = "url"
    collection_name = "toreadlink"

    @gen.coroutine
    def handler(self, body_list, message_id):
        message_id, submessage_id = Service.get_message_id(message_id)
        logging.debug(message_id)
        logging.debug(submessage_id)

        text = body_list.split('\n')
        for i, url in enumerate(text):
            yield self.db[self.db_name][self.collection_name].update(
                {
                    "message_id": message_id,
                    "submessage_id": submessage_id,
                    "link_id": i,
                },
                {
                    "$set":
                    {
                        "message_id": message_id,
                        "submessage_id": submessage_id,
                        "link_id": i,
                        "type": "url",
                        "link": url,
                        "crts": datetime.datetime.utcnow()
                    }
                },
                upsert=True)
