import logging
import ConfigParser

class RequestResponder(object):
    def __init__(self, configFilePath):
        #logging.debug('config: '+configFilePath)
        self._configuration = ConfigParser.RawConfigParser()
        self._configuration.read(configFilePath)
        self.requestHandler = None

    def get(self, requestHandler):
        self.requestHandler = requestHandler

    def post(self, requestHandler):
        self.requestHandler = requestHandler

    def put(self, requestHandler):
        self.requestHandler = requestHandler

    def delete(self, requestHandler):
        self.requestHandler = requestHandler

    def options(self, requestHandler):
        self.requestHandler = requestHandler
