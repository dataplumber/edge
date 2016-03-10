from edge.opensearch.gcmdresponsebysolr import GcmdResponseBySolr

class DatasetGcmdResponse(GcmdResponseBySolr):
    def __init__(self, configuration):
        super(DatasetGcmdResponse, self).__init__(configuration)

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
