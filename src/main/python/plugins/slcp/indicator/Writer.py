import logging
import urllib
import json

from edge.writer.proxywriter import ProxyWriter

class Writer(ProxyWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

    def _generateUrl(self, requestHandler):
        url = self._configuration.get('solr', 'url')
        parameters = {}
        parameters['wt'] = 'json'
        parameters['omitHeader'] = 'true'
        parameters['q'] = '*:*'
        try:
            parameters['fq'] = 'id:"' + requestHandler.get_argument('id') + '"'
        except:
            parameters['fl'] = 'id,name,rate,uncertainties,unit,shortenUnit,abbrUnit'
        try:
            if requestHandler.get_argument('latest').lower() == 'true':
                parameters['fl'] = 'xLatest,yLatest,unit,abbrUnit'
        except:
            pass
        url += '/select?' + urllib.urlencode(parameters)
        logging.debug("proxy to url : " + url)
        return url

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

            solrJson = json.loads(response.body)
            if len(solrJson['response']['docs']) > 1:
                # Need to order indicators accordingly
                solrJsonClone = {}
                solrJsonClone['response'] = {}
                solrJsonClone['response']['start'] = solrJson['response']['start']
                solrJsonClone['response']['numFound'] = solrJson['response']['numFound']
                solrJsonClone['response']['docs'] = []

                indicators = {}
                for doc in solrJson['response']['docs']:
                    indicators[doc['id']] = doc
                for indicator in self._configuration.get('solr', 'ordering').split(','):
                    if indicator in indicators:
                        solrJsonClone['response']['docs'].append(indicators[indicator])
                solrJson = solrJsonClone
            for doc in solrJson['response']['docs']:
                if 'uncertainties' in doc:
                    if doc['id'] in self._configuration.get('solr', 'uncertainties').split(','):
                        doc['uncertainties'] = int(round(doc['uncertainties']))
                        doc['rate'] = int(round(doc['rate']))

            self.requestHandler.write(solrJson)
            self.requestHandler.finish()
