import json
import logging

from edge.response.jsontemplateresponse import JsonTemplateResponse

class Neo4jFacetTemplateResponse(JsonTemplateResponse):
    def __init__(self, facetDefs):
        super(Neo4jFacetTemplateResponse, self).__init__()
        self.facetDefs = facetDefs

    def generate(self, neo4jResponse, pretty=False):
        self._populate(neo4jResponse)
        return super(Neo4jFacetTemplateResponse, self).generate(pretty)

    def _populate(self, neo4jResponse):
        if neo4jResponse is not None:
            neo4jJson = json.loads(neo4jResponse)

            logging.debug('doc count: '+str(len(neo4jJson['response']['docs'])))

            if 'facet_counts' in neo4jJson:
                self.variables['facets'] = neo4jJson['facet_counts']
                self.variables['facetDefs'] = self.facetDefs
