import couchdb,requests,time,uuid,base64,sys

couch = couchdb.Server(sys.argv[2])


def create_request(configuration):
    req = requests.Request(
            configuration['request']['type'],
            configuration['request']['url'],
            data=configuration['request']['payload'],
            headers=configuration['request']['headers'])
    return req.prepare()
    
def save_response(id,response):
    try:
        db = couch['store_{}'.format(id)]
    except:
        db = couch.create('store_{}'.format(id))

    ident = '{}_{}'.format(time.mktime(time.gmtime()),uuid.uuid4())
    try:
        db[ident] = {
                "type": response.headers['Content-Type'],
                "contents": base64.b64encode(response.content).decode()
            }
        return ident
    except Exception as e:
        print('[{}] {}'.format(time.mktime(time.gmtime()),e))
        return False
    

if __name__ == "__main__":
    identifier = sys.argv[1]
    s = requests.Session()
    req = create_request(couch['configurations'][identifier])
    res = s.send(req)
    ident = save_response(identifier,res)
    if ident:
        couch['configurations'][identifier]['last'] = ident
        print("[{}] Successfully made request {}".format(time.mktime(time.gmtime()),identifier))
    else:
        print("[{}] Failed to make request {}".format(time.mktime(time.gmtime()),identifier))

