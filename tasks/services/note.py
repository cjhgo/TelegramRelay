#coding: utf-8
#created at 17-3-7 18:18
import datetime
import logging
from tornado import gen
from ..service import Service, register_service


@register_service
class NoteService(Service):
    name = "note"
    collection_name = "notes"

    @gen.coroutine
    def handler(self, body_list, message_id):
        message_id, submessage_id = Service.get_message_id(message_id)
        logging.debug(message_id)
        logging.debug(submessage_id)

        yield self.db[self.collection_name].update(
                {
                    "message_id": message_id
                },
                {
                    "$set":
                    {
                        "message_id": message_id,
                        "type": "note",
                        "content": body_list.split('\n'),
                        "crts": datetime.datetime.utcnow()
                    }
                },
                upsert=True)