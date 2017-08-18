import couchdb,requests,time,uuid,binascii,sys

couch = couchdb.Server(sys.argv[2])


def create_request(configuration):
    req = requests.Request(
            configuration['type'],
            configuration['url'],
            data=configuration['data'],
            headers=configuration['headers'])
    return s.prepare_request(req)
    
def save_response(id,response):
    try:
        db = couch[id]
    except:
        db = couch.create(id)

    ident = '{}_{}'.format(time.gmtime(),uuid.uuid4())
    try:
        db[ident] = {
                "type": response.headers['Content-Type'],
                "contents": binascii.b2a_base64(response.content)
            }
        return True
    except:
        return False
    

if __name__ == "__main__":
    identifier = sys.argv[1]
    req = create_request(couch['configurations'][identifier])
    res = req.send()
    if save_response(identifier,res):
        print("[{}] Successfully made request {}".format(time.gmtime(),identifier))
    else:
        print("[{}] Failed to make request {}".format(time.gmtime(),identifier))

