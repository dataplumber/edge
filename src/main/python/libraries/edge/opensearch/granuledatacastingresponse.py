import logging

from edge.dateutility import DateUtility
from edge.opensearch.datacastingresponsebysolr import DatacastingResponseBySolr

class GranuleDatacastingResponse(DatacastingResponseBySolr):
    def __init__(self, portalUrl, linkToGranule, archivedWithin):
        super(GranuleDatacastingResponse, self).__init__(portalUrl, archivedWithin)

        self.linkToGranule = linkToGranule.split(',')

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        doc['Granule-StartTimeLong'][0] = DateUtility.convertTimeLongToRFC822(doc['Granule-StartTimeLong'][0])
        doc['Granule-StopTimeLong'][0] = DateUtility.convertTimeLongToRFC822(doc['Granule-StopTimeLong'][0])
        doc['Granule-ArchiveTimeLong'][0] = DateUtility.convertTimeLongToRFC822(doc['Granule-ArchiveTimeLong'][0])
        
        doc['GranuleLink'] = self._getLinkToGranule(doc)
        
        doc['GranuleFileSize'] = dict(zip(doc['GranuleArchive-Type'], doc['GranuleArchive-FileSize']))
        
        if 'GranuleReference-Type' in doc:
            doc['GranuleReference'] = dict([(doc['GranuleReference-Type'][i], doc['GranuleReference-Path'][i]) for i,x in enumerate(doc['GranuleReference-Status']) if x=="ONLINE"])

    def _getLinkToGranule(self, doc):
        link = None

        if 'GranuleReference-Type' in doc and len(self.linkToGranule) > 0:
            granuleRefDict = dict(zip(doc['GranuleReference-Type'], zip(doc['GranuleReference-Path'], doc['GranuleReference-Status'])))

            for type in self.linkToGranule:
                # check if reference type exists
                if type in granuleRefDict:
                    # check if reference is online
                    if granuleRefDict[type][1] == 'ONLINE':
                        link = granuleRefDict[type][0]
                        break

        return link
