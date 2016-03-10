import tornado.httpclient

class HttpUtility(object):
    def getResponse(self, url, callback, body=None):
        if body is not None:
            request = tornado.httpclient.HTTPRequest(url, method='POST', headers={'Connection': 'close'}, request_timeout=30, body=body)
        else:
            request = tornado.httpclient.HTTPRequest(url, method='GET', headers={'Connection': 'close'}, request_timeout=30)
        httpClient = tornado.httpclient.AsyncHTTPClient()
        httpClient.fetch(request,callback=callback)
