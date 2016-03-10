from types import *
import logging
import codecs

import requestresponder
from edge.httputility import HttpUtility

class TemplateResponseWriter(requestresponder.RequestResponder):
    def __init__(self, configFilePath, requiredParams = None):
        super(TemplateResponseWriter, self).__init__(configFilePath)
        if requiredParams is None:
            requiredParams = []
        self.requiredParams = requiredParams
        self.pretty = False

    def get(self, requestHandler):
        super(TemplateResponseWriter, self).get(requestHandler)

        #check required parameters
        for paramList in self.requiredParams:
            countParamNotFound = 0
            for param in paramList:
                try:
                    requestHandler.get_argument(param)
                except:
                    countParamNotFound += 1
            if countParamNotFound == len(paramList):
                raise Exception("One of the following parameters is required: " + ', '.join(paramList))

    def _handleException(self, error):
        self.requestHandler.set_status(404)
        self.requestHandler.write(error)
        self.requestHandler.finish()

    def _readTemplate(self, path):
        file = codecs.open(path, encoding='utf-8')
        data = file.read()
        file.close()

        return data
