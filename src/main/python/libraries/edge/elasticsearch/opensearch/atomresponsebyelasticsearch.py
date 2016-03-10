import json
import urllib

from edge.opensearch.atomresponse import AtomResponse
from collections import defaultdict

class AtomResponseByElasticsearch(AtomResponse):
    def __init__(self):
        super(AtomResponseByElasticsearch, self).__init__()
        self.addNamespace("gibs", "http://gibs.jpl.nasa.gov/opensearch/")

    def generate(self, response, pretty=False):
        self._populate(response)
        return super(AtomResponseByElasticsearch, self).generate(pretty)

    def _populate(self, response):
        self._populateChannel(response)

        if response is None:
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'totalResults', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'startIndex', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'itemsPerPage', 'value': 1}
            )
            self.parameters['startIndex'] = 0
            url = self.link + '?' + urllib.urlencode(self.parameters)
            self.variables.append({'name': 'link', 'attribute': {'href': url, 'rel': 'self', 'type': 'application/atom+xml'}})
            self.variables.append({'name': 'link', 'attribute': {'href': url, 'rel': 'first', 'type': 'application/atom+xml'}})
            item = [
                {'name': 'title', 'value': 'Error'},
                {'name': 'content', 'value': 'error'}
            ]
            self.items.append(item)
        else:
            #logging.debug(response)
            jsonResponse = json.loads(response)
            numFound = int(jsonResponse['hits']['total'])
            start = int(self.parameters['startIndex'])
            rows = int(self.parameters['itemsPerPage'])

            self.parameters['startIndex'] = start
            self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'self', 'type': 'application/atom+xml'}})
            self.parameters['startIndex'] = 0
            self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'first', 'type': 'application/atom+xml'}})
            if start > 0:
                if (start - rows > 0):
                    self.parameters['startIndex'] = start - rows
                self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'previous', 'type': 'application/atom+xml'}})
            if start + rows < numFound:
                self.parameters['startIndex'] = start + rows
                self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'next', 'type': 'application/atom+xml'}})
            
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'totalResults', 'value': numFound}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'startIndex', 'value': start}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'itemsPerPage', 'value': rows}
            )

            for doc in jsonResponse['hits']['hits']:
                item = []
                self._populateItem(response, doc, item)
                self.items.append(item)

    def _populateChannel(self, response):
        pass

    def _populateItem(self, response, doc, item):
        pass
    
    def _populateItemWithAllMetadata(self, doc, item):
        for docKey in doc.keys():
            if isinstance(doc[docKey], list):
                for child in doc[docKey]:
                    childItem = []
                    for childKey in child.keys():
                        childItem.append({'namespace': 'gibs', 'name': childKey, 'value': child[childKey]})
                    item.append({'namespace': 'gibs', 'name': docKey, 'value': childItem})
            else:
                item.append({'namespace': 'gibs', 'name': docKey, 'value': doc[docKey]})
