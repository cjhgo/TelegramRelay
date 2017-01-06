#coding: utf-8
#created at 16-12-27 15:02

import json
import datetime
import logging
import motor
from tornado import  gen
from tornado.ioloop import IOLoop
from tornado.httpclient import  HTTPRequest
try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient
    from tornado.curl_httpclient import curl_log
    curl_log.setLevel(logging.CRITICAL)
except:
    from tornado.httpclient import AsyncHTTPClient as CurlAsyncHTTPClient


logging.getLogger().setLevel(logging.DEBUG)
TelegarmApiUrl = "https://api.telegram.org/bot253258803:AAHsAYENENmKkqNDfxTMimhYuKq5lPbu-dc"
client = motor.MotorClient(max_pool_size=128, tz_aware=True, host="127.0.0.1", port=27017)
db = client.test
db = client.queue


@gen.coroutine
def handle_update(message_type, message_id):
    message_type_to_db = {
        "keyword": "research",
        "url": "toreadlink",
        "note": "notes",
        "todo": "todo",
        "blog": "blog",
    }

    collection_name = message_type_to_db[message_type]
    res = yield db[collection_name].find_one({"message_id": message_id})
    if res:
        yield db[collection_name].remove({"message_id": message_id})


def get_message_id(message_id):
    return tuple(map(int, message_id.split(':')))


@gen.coroutine
def handle_keyword(body_list, message_id):
    message_id, submessage_id = get_message_id(message_id)
    logging.debug(message_id)
    logging.debug(submessage_id)
    body = [item.split('\n') for item in body_list.split('\n\n')]

    yield db.research.update(
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


@gen.coroutine
def handle_toreadlink(body_list, message_id):
    message_id, submessage_id = get_message_id(message_id)
    logging.debug(message_id)
    logging.debug(submessage_id)

    text = body_list.split('\n')
    for i, url in enumerate(text):
        yield db.toreadlink.update(
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


@gen.coroutine
def handle_note(body_list, message_id):
    message_id, submessage_id = get_message_id(message_id)
    logging.debug(message_id)
    logging.debug(submessage_id)

    yield db.notes.update(
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


@gen.coroutine
def handle_todo(body_list, message_id):
    message_id, submessage_id = get_message_id(message_id)
    logging.debug(message_id)
    logging.debug(submessage_id)

    for i, _ in enumerate(body_list):
        yield db.todo.update(
            {
                "message_id": message_id,
                "submessage_id": submessage_id,
                "task_id": i,
            },
            {
                "$set":
                    {
                        "message_id": message_id,
                        "submessage_id": submessage_id,
                        "task_id": i,
                        "type": "todo",
                        "task": _,
                        "crts": datetime.datetime.utcnow()
                    }
            },
            upsert=True)


@gen.coroutine
def handle_blog(body_list, message_id):
    message_id, submessage_id = get_message_id(message_id)
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
    yield db.blog.update(
        {
            "message_id": message_id,
            "submessage_id": submessage_id,
        },
        {
            "$set": meta
        },
        upsert=True)

message_handler = {
    "keyword": handle_keyword,
    "url": handle_toreadlink,
    "note": handle_note,
    "todo": handle_todo,
    "blog": handle_blog,
}


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
            print '\n'.join(links)
            submessage_index = 0
            for texts in content:   # texts: the same kind of message
                texts = texts.splitlines(True)
                message_type = texts.pop(0)[:-1]
                yield handle_update(message_type=message_type, message_id=message_id)
                for text in ''.join(texts).split('\n\n\n'):  # text: one message
                    temp_message_id = ':'.join(map(str, [message_id, submessage_index]))
                    try:
                        yield message_handler[message_type](text, temp_message_id)  #
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


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ioloop.add_callback(run)
    logging.debug("begin!")
    ioloop.start()
