import json

from edge.opensearch.response import Response

class ResponseBySolr(Response):
    def __init__(self):
        super(ResponseBySolr, self).__init__()

    def generate(self, solrResponse):
        self._populate(solrResponse)
        return super(ResponseBySolr, self).generate()

    def _populate(self, solrResponse):
        #response.title = 'OCSI Dataset Search: '+searchText
        #response.description = 'Search result for "'+searchText+'"'
        #response.link = searchUrl
        self._populateChannel(solrResponse)

        if solrResponse is None:
            self.variables.append(
                {'namespace': 'openSearch', 'name': 'totalResults', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'openSearch', 'name': 'startIndex', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'openSearch', 'name': 'itemsPerPage', 'value': 1}
            )
            item = [
                {'name': 'title', 'value': 'Error'},
                {'name': 'description', 'value': 'error'}
            ]
            self.items.append(item)
        else:
            #logging.debug(solrResponse)
            solrJson = json.loads(solrResponse)

            self.variables.append(
                {'namespace': 'openSearch', 'name': 'totalResults', 'value': solrJson['response']['numFound']}
            )
            self.variables.append(
                {'namespace': 'openSearch', 'name': 'startIndex', 'value': solrJson['response']['start']}
            )
            self.variables.append(
                {'namespace': 'openSearch', 'name': 'itemsPerPage', 'value': solrJson['responseHeader']['params']['rows']}
            )

            for doc in solrJson['response']['docs']:
                """
                item = [
                    {'name': 'title', 'value': doc['Dataset-LongName'][0]},
                    {'name': 'description', 'value': doc['Dataset-Description'][0]},
                    {'name': 'link', 'value': self._configuration.get('portal', 'datasetUrl')+'/'+doc['Dataset-ShortName'][0]}
                ]
                """
                item = []
                for docKey in doc.keys():
                    item.append({'namespace': 'podaac', 'name': docKey, 'value': doc[docKey]})

                self._populateItem(solrResponse, doc, item)
                self.items.append(item)

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
