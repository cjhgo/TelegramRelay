#coding: utf-8
#created at 16-12-27 15:02

from functools import partial
import json
import datetime
import logging
import motor
from tornado import  gen, queues
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from common.mytornado.client import CurlAsyncHTTPClient
from common.db import MongoDB, RedisDB
#thoung this is an unused import
#only when you import this module does the service_register decorator will execute
#then the services dict of Service will be populated
import services
from service import Service

from get_title import run as fetch_title
from setting import message_collectionname, botkey


logging.getLogger().setLevel(logging.DEBUG)
TelegarmApiUrl = "https://api.telegram.org/bot" + botkey
client = motor.MotorClient(max_pool_size=128, tz_aware=True, host="127.0.0.1", port=27017)

db = client[message_collectionname]
cache = RedisDB("url")
url_queue = queues.Queue()
fetch_title = partial(fetch_title, url_queue, cache)


@gen.coroutine
def put_url(message):
    text = message["text"]
    for item in message.get("entities",[]):
        if item["type"] == "url":
            begin = item["offset"]
            end = begin + item["length"]
            yield url_queue.put(text[begin:end])


@gen.coroutine
def handle_message(messages, update_id):
    logging.debug("receive message %s", messages)
    data = messages["result"]
    if len(data) > 0:
        for i, message in enumerate(data):
            update_id = message.pop("update_id")
            flag = yield db.TelegramMessage.find_one({"update_id": update_id})
            if flag:
                logging.debug("duplicate message occurs, %s", update_id)
                break

            message = message.get("message", message.get("edited_message"))
            yield put_url(message)
            message_id = message.pop("message_id")
            yield db.TelegramMessage.update(
                {
                    "message_id": message_id
                },
                {
                    "update_id": update_id,
                    "message_id": message_id,
                    "crts": datetime.datetime.utcnow(),
                    "content": message
                },
                upsert=True)
            content = message.get("text", '').split("\n\n\n\n")  # content:all message
            links = filter(lambda x: x[:4] == 'http', message.get("text", '').split("\n"))
            #print '\n'.join(links)
            submessage_index = 0
            for texts in content:   # texts: the same kind of message
                texts = texts.splitlines(True)
                message_type = texts.pop(0)[:-1]
                service = Service.get_service(message_type)
                yield service.handle_update(message_id)
                for text in ''.join(texts).split('\n\n\n'):  # text: one message
                    temp_message_id = ':'.join(map(str, [message_id, submessage_index]))
                    try:
                        yield service.handler(text, temp_message_id)
                    except KeyError as e:
                        logging.debug("unsupported message type occurs %s", e)
                    submessage_index += 1

    IOLoop.current().add_callback(run, update_id)


@gen.coroutine
def run(update_id=0):
    logging.debug(update_id)
    url = TelegarmApiUrl + "/getUpdates?timeout=5&offset=" + str(update_id + 1)
    http_client = CurlAsyncHTTPClient()

    request = HTTPRequest(url, proxy_host='127.0.0.1', proxy_port=8123)
    try:
        try:
            response = yield http_client.fetch(request)
        except NotImplementedError as e:
            request = HTTPRequest(url)
            response = yield http_client.fetch(request)
    except Exception as e:
        logging.debug("something is wrong, %s %s", type(e), e)
        IOLoop.current().add_callback(run, update_id)
    else:
        data = json.loads(response.body)
        yield handle_message(data, update_id)

# todo handle image file
# get path by file id
# https://api.telegram.org/bot253258803:AAHsAYENENmKkqNDfxTMimhYuKq5lPbu-dc/getFile?file_id=AgADBQADKKgxG6A6bQsckUfAJfPJyXwewTIABBW9lEOwuGIRXSMCAAEC
# get real file
# https://api.telegram.org/file/bot253258803:AAHsAYENENmKkqNDfxTMimhYuKq5lPbu-dc/photo/file_1.jpg


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ioloop.add_callback(run)
    logging.debug("begin!")
    ioloop.start()
