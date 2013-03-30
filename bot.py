#!/usr/bin/env python
#

"""
    for sandboxing read:
        http://developer.plone.org/security/sandboxing.html
"""

from werkzeug import Request, ClosingIterator
from werkzeug.exceptions import HTTPException, InternalServerError

from werkzeug import Response

from werkzeug.routing import Map, Rule

from AccessControl.ZopeGuards import get_safe_globals, safe_builtins
from RestrictedPython import compile_restricted

import json

import sys

DEBUG = True

MAGIC = "#!py27"


def build_global(data):
    """
    based on:
        http://developer.plone.org/security/sandboxing.html
    """
    g = get_safe_globals()
    g['__builtins__'] = safe_builtins

    from AccessControl.ImplPython import guarded_getattr as guarded_getattr_safe
    g['_getattr_'] = guarded_getattr_safe
    g['data'] = data
    return g


url_map = Map([
    Rule("/py27", endpoint="py27"),
    Rule("/", endpoint="index"),
])

def index(request):
    return Response("Hello, world!", mimetype="text/plain")

def py27(request):
    """
    {
        "status":"ok",
        "counter":13934721,
        "data":[
            "something for data"
        ],
        "events":[
            {
                "message":{
                    "id":"14333031",
                "room":"bgnori",
                "public_session_id":"IrrMxt",
                "icon_url":"http://www.gravatar.com/avatar/a00efd2efcb4f4efb65f01efd366f4b2.jpg",
                "type":"user",
                "speaker_id":"bgnori",
                "nickname":"bgnori",
                "text":".",
                "timestamp":"2013-03-17T07:38:51Z",
                "local_id":"pending-IrrMxt-4"},
                "event_id":13934721
            }
        ]}
    """
    try:
        data = json.loads(request.data)
    except:
        return Response('bad json', mimetype="text/plain")
  
    
    userdata = None
    for evt in data['events']:
        userdata = evt.get("data", None)
    g = build_global(userdata)
    #print >> sys.stderr, g

    for evt in data['events']:
        msg = evt.get("message", None)
        if msg and msg["text"].startswith(MAGIC):
            source = msg["text"][len(MAGIC)+1:]
            try:
                r = eval(compile_restricted(source, "<string>", "eval"), g)
            except Exception, e:
                return Response(str(e), mimetype="text/plain")
            return Response(str(r), mimetype="text/plain")
        else:
            print >> sys.stderr, "nothing to send"
            break
    return Response('', mimetype="text/plain")

views = {
        'index': index,
        'py27': py27,
        }

class Application(object):
    def __call__(self, environ, start_response):
        try:
            self._setup()
            request = Request(environ)
            if(DEBUG):
                print >> sys.stderr, request.base_url 
                print >> sys.stderr, request.data
            adapter = url_map.bind_to_environ(environ)
            endpoint, values = adapter.match()
            handler = views.get(endpoint)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        except:
            response = InternalServerError()

        return ClosingIterator(response(environ, start_response), self._cleanup)

    def _setup(self):
        pass
    def _cleanup(self):
        pass

from wsgiref.simple_server import make_server

bot = Application()

from werkzeug import DebuggedApplication

#debug = DebuggedApplication(bot)
httpd = make_server('192.168.2.64', 10080, bot)
#httpd = make_server('lingrbot.tonic-water.com', 10080, debug)
httpd.serve_forever()


