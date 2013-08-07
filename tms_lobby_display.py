'''
Created on 1 Aug 2013

@author: Tobias Fischer
'''

import cherrypy
import webbrowser
import os
import json
import tms_connector

MEDIA_DIR = os.path.join(os.path.abspath("."), u"static")

class AjaxApp(object):
    @cherrypy.expose
    def index(self):
        return open(os.path.join(MEDIA_DIR, u'index.html'))

    @cherrypy.expose
    def submit(self, name):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(dict(title="Hello, %s" % name))

    #this actually runs read_tms() and responds it to browser
    @cherrypy.expose
    def getmovies(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return tms_connector.read_tms()

# this content is directly delivered to browser
config = {'/static':
        {'tools.staticdir.on': True,
         'tools.staticdir.dir': MEDIA_DIR,
        }
}

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8000,
                       })

#helper for development: open web browser after starting application
def open_page():
    webbrowser.open("http://127.0.0.1:8000/")
cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(AjaxApp(), '/', config=config)
cherrypy.engine.start()
