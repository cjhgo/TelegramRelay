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
def handle_keyword(body_list, update_id):
    body = [item.split('\n') for item in body_list.split('\n\n')]
    yield db.research.insert({
        "type": "keyword",
        "message_id": update_id,
        "content": body[0],
        "urls": body[1] if len(body) > 1 else [],
        "crts": datetime.datetime.utcnow()
    })


@gen.coroutine
def handle_toreadlink(body_list, update_id):
    text = body_list.split('\n')
    for url in text:
        yield db.toreadlink.insert({
            "message_id": update_id,
            "type": "url",
            "link": url,
            "crts": datetime.datetime.utcnow()
        })


@gen.coroutine
def handle_note(body_list, update_id):
    yield db.notes.insert(
        {
            "message_id": update_id,
            "type": "note",
            "content": "\n".join(body_list),
            "crts": datetime.datetime.utcnow()
        }
    )


@gen.coroutine
def handle_todo(body_list, update_id):
    for _ in body_list:
        yield db.todo.insert({
            "message_id": update_id,
            "type": "todo",
            "task": _,
            "crts": datetime.datetime.utcnow()
        })


@gen.coroutine
def handle_blog(body_list, update_id):
    items = body_list.split('\n')
    url = items.pop(0)
    meta = {}
    for _ in items:
        key, value = _.split(': ', 1)
        meta[key] = value
    yield db.blog.insert({
        "message_id": update_id,
        "url": url,
        "source": meta.get("source"),
        "about": meta.get("about"),
        "description": meta.get("description"),
        "crts": datetime.datetime.utcnow(),
    })

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
        update_id = data[-1].get("update_id")
        for message in data:
            flag = yield db.TelegramMessage.find_one({"message_id": update_id})
            if flag:
                logging.debug("duplicate message occurs, %s", update_id)
                break
            yield db.TelegramMessage.insert({
                "message_id": update_id,
                "crts": datetime.datetime.utcnow(),
                "content": message["message"]
            })
            content = message["message"].get("text", '').split("\n\n\n\n")  # content:all message
            links = filter(lambda x: x[:4] == 'http', message["message"].get("text", '').split("\n"))
            print links
            for texts in content:   # texts: the same kind of message
                texts = texts.splitlines(True)
                message_type = texts.pop(0)[:-1]
                for text in ''.join(texts).split('\n\n\n'):  # text: one message
                    try:
                        yield message_handler[message_type](text, update_id)  #
                    except KeyError as e:
                        logging.debug("unsupported message type occurs %s", e)

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
        logging.debug("something is wrong, %s %s", type(e),e)
        IOLoop.current().add_callback(run, update_id)
    else:
        data = json.loads(response.body)
        yield handle_message(data, update_id)


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ioloop.add_callback(run)
    logging.debug("begin!")
    ioloop.start()
