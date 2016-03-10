import datetime
import pycurl
from StringIO import StringIO
import json
import logging
import urllib
import os.path

from edge.opensearch.templateresponse import TemplateResponse

class SolrCmrTemplateResponse(TemplateResponse):
    def __init__(self, configuration, link, parameters):
        super(SolrCmrTemplateResponse, self).__init__()
        self._configuration = configuration
        self.link = link
        self.parameters = parameters

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(SolrCmrTemplateResponse, self).generate(pretty)

    def _get_cmr_response(self, url, cmr):

        # Execute the curl command and load the json object.
        buffer = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()
        except:
            output = '{ "errors": "%s" }' %(c.errstr())
            c.close()
        else:
            try:
                output = json.loads(buffer.getvalue())
            except:
                output = '{ "errors": "json loads failed: [%s]" }' %(buffer.getvalue())
     
        # Format the output if there are errors.
        response = {}
        if output.keys().__contains__('errors'):
            response['entry'] = []
            response['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response['id'] = url
            if url.find('collections') != -1:
                response['title'] = 'ECHO dataset metadata'
            elif url.find('granules') != -1:
                response['title'] = 'ECHO granule metadata'
            response['errors'] = output['errors'][0]
        else:
            response = output

        try:

            if response.keys().__contains__('errors'):
                return(response)
    
            if not(response.keys().__contains__('feed')):
                raise ValueError('no "feed" in the cmr response')
            if not(response['feed'].keys().__contains__('entry')):
                raise ValueError('no "entry" in the cmr response')
            if not(response['feed'].keys().__contains__('updated')):
                raise ValueError('no "updated" key in the cmr response')
            if not(response['feed'].keys().__contains__('id')):
                raise ValueError('no "id" key in the cmr response')
            if not(response['feed'].keys().__contains__('title')):
                raise ValueError('no "id" key in the cmr response')
      
            # Create lists if they do not exists.
            if not(cmr.keys().__contains__('cmr_search_updated')):
                cmr['cmr_search_updated'] = []
            if not(cmr.keys().__contains__('cmr_search_url')):
                cmr['cmr_search_url'] = []
            if not(cmr.keys().__contains__('cmr_search_title')):
                cmr['cmr_search_title'] = []

            cmr['cmr_search_updated'].append(response['feed']['updated'])
            cmr['cmr_search_url'].append(response['feed']['id'])
            cmr['cmr_search_title'].append(response['feed']['title'])

            # Create list objects for the "entry" key.
            if response['feed']['entry'] != []:
                entry = response['feed']['entry'][0]
                for key in entry:
                    keyname = 'cmr_%s' %(key)
                    if not(cmr.keys().__contains__(keyname)):
                        cmr[keyname] = []
                    cmr[keyname].append(entry[key])
    
        except ValueError, e:
            msg = 'Error! parse error: %s.' %e
            print '%s\n' %msg
    
        return(cmr)

    def _populate(self, solrResponse):
        self.variables['link'] = self.link

        start = 0
        rows = 0
        numFound = 0
        
        if solrResponse is not None:
            solrJson = json.loads(solrResponse)

            logging.debug('Total doc count: '+str(solrJson['response']['numFound']))
            logging.debug('Total item count: '+ str(len(solrJson['response']['docs'])))

            #----------------------------------------------------------------------------------------------
            # CMR: Processing 
            #----------------------------------------------------------------------------------------------
            cmr_total_time = datetime.timedelta(0)
            cmr_total_count = 0

            for i in range(len(solrJson['response']['docs'])):

                doc = solrJson['response']['docs'][i]
                logging.debug('doc[id]: '+str(doc['id']))

                #------------------------------------------------------------------------------------------
                # CMR: Initialize 
                #------------------------------------------------------------------------------------------
                cmr = {}

                #------------------------------------------------------------------------------------------
                # CMR: PRODUCT_TYPE
                #------------------------------------------------------------------------------------------

                if solrJson['response']['docs'][i].keys().__contains__('product_type_dataset_short_name_list'):

                    for j in range(len(doc['product_type_dataset_short_name_list'])):

                        cmr_test = 0
                        if cmr_test == 1:
                           cmr_search_url = 'https://cmr.earthdata.nasa.gov/search/collections.json?keyword=NSIDC'
                        else:
                           cmr_search_url = 'https://cmr.earthdata.nasa.gov/search/collections.json?keyword=' + \
                                             doc['product_type_dataset_short_name_list'][j]

                        logging.debug('cmr search url: ' +cmr_search_url)
                        time1 = datetime.datetime.now()
                        cmr = self._get_cmr_response(cmr_search_url, cmr) 
                        time2 = datetime.datetime.now()
                        time3 = time2 - time1
                        logging.debug('cmr search time: ' + time3.__str__() + ' 1 product_type')

                        cmr_total_time = cmr_total_time + time3
                        cmr_total_count = cmr_total_count + 1
                        
                #------------------------------------------------------------------------------------------
                # CMR: PRODUCT (Only search when the query contains 'id' - ie individual cmr search)
                #------------------------------------------------------------------------------------------

                elif solrJson['response']['docs'][i].keys().__contains__('product_granule_remote_granule_ur_list') and \
                     self.parameters.keys().__contains__('id'):

                    for j in range(len(doc['product_granule_remote_granule_ur_list'])):

                        cmr_test = 0
                        if cmr_test == 1:
                           cmr_search_url = 'https://cmr.earthdata.nasa.gov/search/granules.json?granule_ur[]=' + \
                                            '20070106-NAR18_SST-EUR-L2P-sst1nar_noaa18_20070106_asc-v01.nc'
                        else:
                           cmr_search_url = 'https://cmr.earthdata.nasa.gov/search/granules.json?granule_ur[]=' + \
                                             doc['product_granule_remote_granule_ur_list'][j]

                        logging.debug('cmr search url: ' +cmr_search_url)
                        time1 = datetime.datetime.now()

                        cmr = self._get_cmr_response(cmr_search_url, cmr) 

                        time2 = datetime.datetime.now()
                        time3 = time2 - time1
                        logging.debug('cmr search time: ' + time3.__str__() + ' 1 product')

                        cmr_total_time = cmr_total_time + time3
                        cmr_total_count = cmr_total_count + 1

                #------------------------------------------------------------------------------------------
                # CMR: Docs not containing CMR search related criteria
                #------------------------------------------------------------------------------------------
                else:
                    continue

                #------------------------------------------------------------------------------------------
                # CMR: Post-processing
                #------------------------------------------------------------------------------------------
                if cmr != {}:
                    doc.update(cmr)
                    #print json.dumps(cmr, indent=4)
                else:
                    logging.debug('***>>> cmr was not set')
                #------------------------------------------------------------------------------------------
                # CMR: End
                #------------------------------------------------------------------------------------------

            self.variables['docs'] = solrJson['response']['docs']
            self.variables['numFound'] = solrJson['response']['numFound']
            self.variables['itemsPerPage'] = solrJson['responseHeader']['params']['rows']
            self.variables['startIndex'] = solrJson['response']['start']
            self.variables['updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
            
            start = int(solrJson['response']['start'])
            rows = int(solrJson['responseHeader']['params']['rows'])
            numFound = int(solrJson['response']['numFound'])

            logging.debug('Num docs found: ' + str(self.variables['numFound']))
            logging.debug('Items per page: ' + str(self.variables['itemsPerPage']))

            # Show CMR statistics.
            cmr_type = ''
            if os.path.basename(self.variables['link']) == 'product_type':
               cmr_type = 'dataset'
            elif os.path.basename(self.variables['link']) == 'product':
               cmr_type = 'granule'
            if (cmr_type == 'dataset' or cmr_type == 'granule') and cmr_total_count != 0:
                cmr_average_time = cmr_total_time/cmr_total_count
                cmr_stats_msg = 'CMR search results: %s total per/%d %s(s)   %s average per/%s' \
                                %(cmr_total_time.__str__(), cmr_total_count, cmr_type, cmr_average_time.__str__(), cmr_type)
                logging.debug(cmr_stats_msg)
           
            if 'facet_counts' in solrJson:
                self.variables['facets'] = solrJson['facet_counts']

        self.parameters['startIndex'] = start
        self.variables['myself'] = self.link + '?' + urllib.urlencode(self.parameters, True)
        
        if rows != 0:
            self.parameters['startIndex'] = numFound - (numFound % rows)
        self.variables['last'] = self.link + '?' + urllib.urlencode(self.parameters, True)
        
        self.parameters['startIndex'] = 0
        self.variables['first'] = self.link + '?' + urllib.urlencode(self.parameters, True)
        if start > 0:
            if (start - rows > 0):
                self.parameters['startIndex'] = start - rows
            self.variables['prev'] = self.link + '?' + urllib.urlencode(self.parameters, True)
            
        if start + rows < numFound:
            self.parameters['startIndex'] = start + rows
            self.variables['next'] = self.link + '?' + urllib.urlencode(self.parameters, True)
