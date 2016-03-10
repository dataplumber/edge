import logging
import urllib

from edge.dateutility import DateUtility
from edge.writer.proxywriter import ProxyWriter

class Writer(ProxyWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

    def _generateUrl(self, requestHandler):
        url = self._configuration.get('solr', 'url')
        parameters = {}
        parameters['wt'] = 'json'
        parameters['group'] = 'true'
        parameters['group.limit'] = -1
        #parameters['facet.limit'] = 10
        parameters['fl'] = 'time,productTypePrefix,productType'
        parameters['group.field'] = 'crid'
        parameters['omitHeader'] = 'true'
        parameters['q'] = '*:*'
        parameters['fq'] = []
        parameters['sort'] = 'crid desc'
        try:
            parameters['fq'].append('collection:"' + requestHandler.get_argument('collection') + '"')
        except:
            pass
        try:
            parameters['fq'].append('productType:"' + requestHandler.get_argument('productType') + '"')
        except:
            pass
        try:
            start = requestHandler.get_argument('start')
            if len(start) == 10:
                start += 'T00:00:00'
        except:
            raise Exception('Missing start parameter.')
        try:
            end = requestHandler.get_argument('end')
            if len(end) == 10:
                end += 'T23:59:59'
        except:
            end = start[0:10] + 'T23:59:59'

        logging.debug('start: ' + start)
        logging.debug('end: ' + end)

        start = DateUtility.convertISOToUTCTimestamp(start)
        end = DateUtility.convertISOToUTCTimestamp(end) + 999
        parameters['fq'].append('time:[' + str(start) + ' TO ' + str(end) + ']')

        url += '/select?' + urllib.urlencode(parameters, True)
        logging.debug("proxy to url : " + url)
        return url
