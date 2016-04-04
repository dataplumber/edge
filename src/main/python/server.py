import tornado.httpserver
import tornado.ioloop
import tornado.web

import logging
import logging.config
import os
import ConfigParser
import socket

import pluginhandler

class GenericHandler(tornado.web.RequestHandler):
    def initialize(self, pluginName, format=None):
        super(GenericHandler, self).initialize()
        self._pluginHandler = pluginhandler.PluginHandler(pluginName, 'plugins', format)

    @tornado.web.asynchronous
    def get(self):
        self._handleRequest('get')

    def _handleRequest(self, httpMethod):
        try:
            #logging.debug("_handleRequest")
            self._pluginHandler.handleRequest(httpMethod, self.request.path, self)
        except BaseException as exception:
            logging.exception('something is wrong with this plugin: '+str(exception))

            self.set_status(404)
            self.write('something is wrong with this plugin: '+str(exception))
            self.finish()

class TemplateRenderHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/xml")
        try:
            fileName = self.request.path.split('/').pop()
            self.render(fileName)
        except BaseException as exception:
            self.set_header("Content-Type", "text/html")
            self.set_status(404)
            self.write('File not found '+fileName)

if __name__ == "__main__":
    #logging.basicConfig(filename="log.txt",level=logging.DEBUG)
    logging.config.fileConfig(r'./logging.conf')

    configuration = ConfigParser.RawConfigParser()
    configuration.read(r'./config.conf')

    settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"), static_url_prefix="/static/", template_path=os.path.join(os.path.dirname(__file__), "templates"))
    application = tornado.web.Application([
        #(r"/dataset/.*", DatasetHandler),
        (r"/ws/search/samos", GenericHandler, dict(pluginName='samos', format=['json'])),
        (r"/ws/search/icoads", GenericHandler, dict(pluginName='icoads', format=['json'])),
        (r"/ws/search/spurs", GenericHandler, dict(pluginName='spurs', format=['json'])),
        (r"/nexus/climatology", GenericHandler, dict(pluginName='nexus', format=['climatology'])),
        (r"/nexus/solr", GenericHandler, dict(pluginName='nexus', format=['solr'])),
        (r"/nexus/subsetter", GenericHandler, dict(pluginName='nexus', format=['subsetter'])),
        (r"/ws/search/dataset", GenericHandler, dict(pluginName='slcp', format=['atom'])),
        (r"/ws/search/granule", GenericHandler, dict(pluginName='slcp', format=['granule'])),
        (r"/ws/facet/dataset", GenericHandler, dict(pluginName='slcp', format=['facet'])),
        (r"/ws/suggest/dataset", GenericHandler, dict(pluginName='slcp', format=['suggest'])),
        (r"/ws/metadata/dataset", GenericHandler, dict(pluginName='slcp', format=['echo10'])),
        (r"/ws/indicator/dataset", GenericHandler, dict(pluginName='slcp', format=['indicator'])),
        (r"/ws/search/content", GenericHandler, dict(pluginName='slcp', format=['content'])),
        (r"/tie/collection", GenericHandler, dict(pluginName='tie', format=['collection'])),
        #(r"/ws/metadata/dataset", DatasetHandler, dict(format=['iso', 'gcmd'])),
        #(r"/granule/.*", GranuleHandler),
        #(r"/ws/search/granule", GenericHandler, dict(pluginName='product', format=['atom'])),
        #(r"/ws/metadata/granule", GranuleHandler, dict(format=['iso', 'fgdc', 'datacasting'])),
        (r"/passthrough/.*", GenericHandler, dict(pluginName='passthrough')),
        (r"/ws/search/.*", TemplateRenderHandler)
    ], default_host=configuration.get('server', 'host'), **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(
        configuration.getint('server', 'port')
    )
    ioLoop = tornado.ioloop.IOLoop.instance()
    try:
        logging.info('tornado is started.')
        ioLoop.start()
    except KeyboardInterrupt:
        logging.info('tornado is shutting down.')
        ioLoop.stop()
