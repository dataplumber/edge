import logging

import requestresponder
from edge.httputility import HttpUtility

class ProxyWriter(requestresponder.RequestResponder):
    def __init__(self, configFilePath):
        super(ProxyWriter, self).__init__(configFilePath)

    def get(self, requestHandler):
        super(ProxyWriter, self).get(requestHandler)
        try:
            httpUtility = HttpUtility()
            result = httpUtility.getResponse(self._generateUrl(requestHandler), self.onResponse)
        except BaseException as exception:
            raise exception

    def onResponse(self, response):
        if response.error:
            self.requestHandler.set_status(404)
            self.requestHandler.write(str(response.error))
            self.requestHandler.finish()
        else:
            for name, value in response.headers.iteritems():
                logging.debug('header: '+name+':'+value)
                self.requestHandler.set_header(name, value)
            self.requestHandler.set_header('Access-Control-Allow-Origin', '*')
            self.requestHandler.write(response.body)
            self.requestHandler.finish()

    def _generateUrl(self, requestHandler):
        pass
