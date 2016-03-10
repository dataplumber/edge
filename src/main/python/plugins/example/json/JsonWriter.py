import requestresponder

class JsonWriter(requestresponder.RequestResponder):
    def get(self, requestHandler):
        requestHandler.write('{"test": "aaa"}')
        
