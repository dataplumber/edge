import tornado.httpclient

class HttpUtility(object):
    def getResponse(self, url, callback, body=None, json=False):
        headers = {'Connection': 'close'}
        if json:
            headers['Content-Type'] = 'application/json; charset=UTF-8'
        if body is not None:
            request = tornado.httpclient.HTTPRequest(url, method='POST', headers=headers, request_timeout=30, body=body)
        else:
            request = tornado.httpclient.HTTPRequest(url, method='GET', headers=headers, request_timeout=30)
        httpClient = tornado.httpclient.AsyncHTTPClient()
        httpClient.fetch(request,callback=callback)
