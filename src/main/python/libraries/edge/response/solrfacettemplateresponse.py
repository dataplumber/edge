import json
import logging

from edge.response.jsontemplateresponse import JsonTemplateResponse

class SolrFacetTemplateResponse(JsonTemplateResponse):
    def __init__(self, facetDefs):
        super(SolrFacetTemplateResponse, self).__init__()
        self.facetDefs = facetDefs

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(SolrFacetTemplateResponse, self).generate(pretty)

    def _populate(self, solrResponse):
        if solrResponse is not None:
            solrJson = json.loads(solrResponse)

            logging.debug('doc count: '+str(len(solrJson['response']['docs'])))

            if 'facet_counts' in solrJson:
                self.variables['facets'] = solrJson['facet_counts']
                self.variables['facetDefs'] = self.facetDefs
