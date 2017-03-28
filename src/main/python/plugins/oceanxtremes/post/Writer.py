import logging
import urllib2
import urlparse

import requestresponder
from edge.httputility import HttpUtility

class Writer(requestresponder.RequestResponder):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

    def post(self, requestHandler):
        super(Writer, self).get(requestHandler)
        print requestHandler.request.body
        print 'hello world'
        httpUtility = HttpUtility()
        solrUrl = self._configuration.get('solr', 'url') + "/update/json/docs?commit=true"
        result = httpUtility.getResponse(solrUrl, self.onResponse, body=requestHandler.request.body, headers={'Content-Type': 'application/json'})

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
