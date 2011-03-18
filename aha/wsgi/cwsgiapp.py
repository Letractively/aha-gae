# -*- coding: utf-8 -*-
# cwsgiapp.py
# Custom webapp.WSGIApplication, passing through exception on debug mode
#     so that werkzeug can handle one.

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


from google.appengine.ext.webapp import WSGIApplication, RequestHandler
from wsgiref.handlers import CGIHandler
from aha.dispatch import dispatcher

class CWSGIApplication(WSGIApplication):
    def __call__(self, environ, start_response):
        """Called by WSGI when a request comes in."""

        def handle_request(handler, environ):
            """
            Internal function to handle request
            """
            method = environ['REQUEST_METHOD']
            if method == 'GET':
                handler.get(*groups)
            elif method == 'POST':
                handler.post(*groups)
            elif method == 'HEAD':
                handler.head(*groups)
            elif method == 'OPTIONS':
                handler.options(*groups)
            elif method == 'PUT':
                handler.put(*groups)
            elif method == 'DELETE':
                handler.delete(*groups)
            elif method == 'TRACE':
                handler.trace(*groups)
            else:
                handler.error(501)

        request = self.REQUEST_CLASS(environ)
        response = self.RESPONSE_CLASS()

        WSGIApplication.active_instance = self

        handler = None
        groups = ()
        for regexp, handler_class in self._url_mapping:
            match = regexp.match(request.path)
            if match:
                handler = handler_class()
                handler.initialize(request, response)
                groups = match.groups()
                break

        self.current_request_args = groups

        if handler:
            if self._WSGIApplication__debug:
                # debug mode
                handle_request(handler, environ)
            else:
                # production mode
                try:
                    handle_request(handler, environ)
                except Exception, e:
                    handler.handle_exception(e, self._WSGIApplication__debug)
        else:
            response.set_status(404)

        response.wsgi_write(start_response)
        return ['']


class CustomHandler(CGIHandler):
    """
    wsgiref.handlers.CGIHandler holds os.environ when imported.
    This class override this behaviour.
    """
    def init(self):
        self.os_environ = {}
        CGIHandler.init(self)

class MainHandler(RequestHandler):
    """Handles all requests
    """
    def __init__(self):
        """
        A initialization function.
        You can set config.dispatcher parameter to use custom dispatcher.
        In case it is None, it uses default aha.dispatch.dispatcher.
        """
        super(MainHandler, self).__init__(self)
        from aha import Config
        config = Config()
        if hasattr(config, 'dispatcher'):
            self.dispatcher = config.dispatcher;
        else:
            self.dispatcher = dispatcher;

    def get(self, *args):
        self.__process_request()

    def post(self, *args):
        self.__process_request()
        
    def head(self, *args):
        self.__process_request()
        
    def options(self, *args):
        self.__process_request()
        
    def put(self, *args):
        self.__process_request()
        
    def delete(self, *args):
        self.__process_request()
        
    def trace(self, *args):
        self.__process_request()

    def __process_request(self):
        """dispatch the request"""
        self.dispatcher.dispatch(self)

    def handle_exception(self, exception, debug_mode):
        from aha import Config
        config = Config()
        if config.template_lookup and config.error_template:
            # get error template in config and make response by using it.
            t = config.template_lookup.get_template(config.error_template)
            result = t.render()
            self.response.out.write(result)
        else:
            # make output as normal exception
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(exception)

