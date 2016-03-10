import logging
import urllib

from edge.writer.proxywriter import ProxyWriter

class GenericProxyWriter(ProxyWriter):
    def __init__(self, configFilePath):
        super(GenericProxyWriter, self).__init__(configFilePath)

    def _generateUrl(self, requestHandler):
        url = self._configuration.get('proxy', 'url')
        url += requestHandler.request.uri[requestHandler.request.uri.index("?"):]
        logging.debug("proxy to url : " + url)
        return url
