import logging
import urllib2
import urlparse

import requestresponder
from edge.httputility import HttpUtility

class PassThroughWriter(requestresponder.RequestResponder):
    def __init__(self, configFilePath):
        super(PassThroughWriter, self).__init__(configFilePath)

    def get(self, requestHandler):
        super(PassThroughWriter, self).get(requestHandler)
        url = None
        try:
            url = requestHandler.get_argument('url')
        except:
            raise Exception('Missing url.')

        if self._isAllowed(url) == False:
            raise Exception('Not allowed to connect to that url: '+url)

        #io = None
        try:
            """
            logging.debug('url: '+url)
            io = urllib2.urlopen(url)

            message = io.info()
            for headerEntry in message.headers:
                pair = headerEntry.split(':')
                logging.debug('key: '+pair[0]+', value: '+pair[1].replace('\r\n', ''))
                requestHandler.set_header(pair[0], pair[1].replace('\r\n', ''))

            while True:
                data = io.read()
                if data == '':
                    break
                else:
                    requestHandler.write(data)
            """
            
            httpUtility = HttpUtility()
            result = httpUtility.getResponse(url, self.onResponse)
            """
            for header in result['header']:
                logging.debug('header: '+header[0]+':'+header[1])
                requestHandler.set_header(header[0], header[1])

            requestHandler.write(result['data'])
            """
        except BaseException as exception:
            raise exception
        """
        finally:
            if io is not None:
                io.close()
        """

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
            self.requestHandler.write(response.body)
            self.requestHandler.finish()
        
    def _isAllowed(self, url):
        allow = self._configuration.get('service', 'allow')
        allows = allow.split(',')
        for i in range(len(allows)):
            allows[i] = allows[i].strip()

        """
        for value in allows:
            logging.debug('allow: '+value)
        """

        segments = urlparse.urlparse(url)
        netlocation = segments.netloc

        targets = [netlocation]
        netlocations = netlocation.split(':')
        if len(netlocations) == 2:
            if netlocations[1] == '80':
                targets.append(netlocations[0])

        """
        for element in targets:
            logging.debug('target: '+element)
        """

        isAllowed = False
        for target in targets:
            for element in allows:
                if target == element:
                    isAllowed = True
                    break

        return isAllowed
