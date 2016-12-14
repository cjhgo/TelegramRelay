#coding:utf-8
#created by chen @2016/9/17 17:11
import sys
import json
from tornado.concurrent import Future, TracebackFuture
from tornado.web import RequestHandler, HTTPError, _has_stream_request_body
from tornado import gen, iostream
from tornado.gen import coroutine, Return
from tornado.log import access_log, app_log, gen_log

class ApiHTTPError(HTTPError):
    def __init__(self, status_code, log_message, data = {}, *args, **kwargs):
        super(ApiHTTPError,self).__init__(status_code, log_message, *args, **kwargs)

        self.data = data


class ServerError(ApiHTTPError):
    def __init__(self, log_message, status_code=500, data={}, *args, **kwargs):
        if not isinstance(log_message, basestring):
            log_message = log_message.__str__() if isinstance(log_message, HTTPError) else repr(log_message)
        super(ServerError, self).__init__(status_code, log_message, *args, **kwargs)


class RequestHandler(RequestHandler):
    def response(self, result):
        result = {
            "status": 0 if not isinstance(result, HTTPError) else result.status_code,
            "msg": '' if not isinstance(result, HTTPError) else result.log_message or 'Unknown',
            "data": result if not isinstance(result, HTTPError) else {},
        }
        data = json.dumps(result, default=str, ensure_ascii=False).encode("utf-8")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.api_status = result["status"]
        self.api_msg = result["msg"]
        self.response_len = len(data)
        self.finish(data)

    @gen.coroutine
    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict((k, self.decode_argument(v, name=k))
                                    for (k, v) in kwargs.items())
            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in ("GET", "HEAD", "OPTIONS") and \
                    self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()

            result = self.prepare()
            if result is not None:
                result = yield result
            if self._prepared_future is not None:
                # Tell the Application we've finished with prepare()
                # and are ready for the body to arrive.
                self._prepared_future.set_result(None)
            if self._finished:
                return

            if _has_stream_request_body(self.__class__):
                # In streaming mode request.body is a Future that signals
                # the body has been completely received.  The Future has no
                # result; the data has been passed to self.data_received
                # instead.
                try:
                    yield self.request.body
                except iostream.StreamClosedError:
                    return

            method = getattr(self, self.request.method.lower())
            result = method(*self.path_args, **self.path_kwargs)
            if result is not None:
                result = yield result
            if self._auto_finish and not self._finished:
                self.response(result)
        except Exception as e:
            try:
                self._handle_request_exception(e)
            except Exception:
                app_log.error("Exception in exception handler", exc_info=True)
            if (self._prepared_future is not None and
                    not self._prepared_future.done()):
                # In case we failed before setting _prepared_future, do it
                # now (to unblock the HTTP server).  Note that this is not
                # in a finally block to avoid GC issues prior to Python 3.4.
                self._prepared_future.set_result(None)

    def _handle_request_exception(self, e):
        if self._finished:
            return
        if isinstance(e, HTTPError):
            self.response(e)
        else:
            # self.response(ServerError(e))
            self.response(HTTPError(log_message=repr(e)))

