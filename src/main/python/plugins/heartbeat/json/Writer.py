import logging
import json

import requestresponder
from edge.httputility import HttpUtility

class Writer(requestresponder.RequestResponder):
    url = None

    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)
        self.url = self._configuration.get('solr', 'url') + "/admin/ping"

    def get(self, requestHandler):
        super(Writer, self).get(requestHandler)
        try:
            httpUtility = HttpUtility()
            result = httpUtility.getResponse(self.url, self.onResponse)
        except BaseException as exception:
            raise exception

    def onResponse(self, response):
        self.requestHandler.set_header("Content-Type", "application/json")
        self.requestHandler.set_header('Access-Control-Allow-Origin', '*')
        if response.error:
            self.requestHandler.write(json.dumps({"online": False}))
            self.requestHandler.finish()
        else:
            self.requestHandler.write(json.dumps({"online": True}))
            self.requestHandler.finish()
