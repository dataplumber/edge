import logging
import urllib

from edge.writer.proxywriter import ProxyWriter

class Writer(ProxyWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

    def _generateUrl(self, requestHandler):
        url = self._configuration.get('solr', 'url')
        parameters = {}
        parameters['wt'] = 'json'
        parameters['suggest'] = 'true'
        #parameters['suggest.build'] = 'true'
        try:
            parameters['suggest.q'] = requestHandler.get_argument('keyword')
            url += '/suggest?' + urllib.urlencode(parameters)
        except:
            raise Exception('Missing keyword parameter.')
        logging.debug("proxy to url : " + url)
        return url
