import logging
import urllib2
import urlparse
import uuid
import json
from datetime import datetime

import requestresponder
from edge.httputility import HttpUtility

class Writer(requestresponder.RequestResponder):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

    def options(self, requestHandler):
        super(Writer, self).options(requestHandler)
        self.requestHandler.set_header('Access-Control-Allow-Origin', '*')
        self.requestHandler.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.requestHandler.set_header('Access-Control-Allow-Headers', 'Content-Type')
        self.requestHandler.set_header('Allow', 'OPTIONS, GET, HEAD, POST')
        self.requestHandler.set_header('Accept', 'application/json')
        self.requestHandler.set_status(200)
        self.requestHandler.finish()

    def post(self, requestHandler):
        super(Writer, self).post(requestHandler)
        data = json.loads(requestHandler.request.body)

        data["id"] = str(uuid.uuid4())
        data["submit_date"] = datetime.utcnow().isoformat() + "Z"

        httpUtility = HttpUtility()
        solrUrl = self._configuration.get('solr', 'url') + "/update/json/docs?commit=true"
        result = httpUtility.getResponse(solrUrl, self.onResponse, body=json.dumps(data), headers={'Content-Type': 'application/json'})

    def onResponse(self, response):
        self.requestHandler.set_header('Access-Control-Allow-Origin', '*')
        if response.error:
            self.requestHandler.set_status(404)
            self.requestHandler.write(str(response.error))
            self.requestHandler.finish()
        else:
            self.requestHandler.write(response.body)
            self.requestHandler.finish()
