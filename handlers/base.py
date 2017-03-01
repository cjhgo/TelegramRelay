#coding:utf-8
#created by chen @2016/9/17 17:11
import sys
import json
import functools
from tornado.concurrent import Future, TracebackFuture
from tornado.web import RequestHandler, HTTPError, _has_stream_request_body, Finish
from tornado import gen, iostream
from tornado.gen import coroutine, Return
from tornado.log import access_log, app_log, gen_log

class ApiHTTPError(HTTPError):
    def __init__(self, status_code, log_message, data={}, *args, **kwargs):
        super(ApiHTTPError,self).__init__(status_code, log_message, *args, **kwargs)

        self.data = data

class ForbiddenError(ApiHTTPError):
    def __init__(self, log_message, status_code=300, data={},  *args, **kwargs):
        super(ForbiddenError, self).__init__(status_code, log_message, data, *args, **kwargs)


class ServerError(ApiHTTPError):
    def __init__(self, log_message, status_code=500, data={}, *args, **kwargs):
        if not isinstance(log_message, basestring):
            log_message = log_message.__str__() if isinstance(log_message, HTTPError) else repr(log_message)
        super(ServerError, self).__init__(status_code, log_message, *args, **kwargs)


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(403, log_message=u"用户未登录")
        return method(self, *args, **kwargs)
    return wrapper


class RequestHandler(RequestHandler):
    def response(self, result):
        if not isinstance(result, HTTPError):
            msg = ''
        elif not result.log_message:
            msg = str(result)
        else:
            msg = result.log_message
        result = {
            "status": 0 if not isinstance(result, HTTPError) else result.status_code,
            "msg": msg,
            "data": result if not isinstance(result, HTTPError) else {},
        }
        # data = json.dumps(result, default=str, ensure_ascii=False).decode("utf-8")
        data = json.dumps(result, default=str)
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

    def get_current_user(self):
        acookie = self.get_secure_cookie("acookie")
        if not acookie:
            return None
        return acookie

    def _handle_request_exception(self, e):
        if isinstance(e, Finish):
            # Not an error; just finish the request without logging.
            if not self._finished:
                self.finish(*e.args)
            return
        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            app_log.error("Error in exception logger", exc_info=True)
        if self._finished:
            return
        if isinstance(e, HTTPError):
            self.response(e)
        else:
            self.response(HTTPError(log_message=repr(e)))
