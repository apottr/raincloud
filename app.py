from flask import Flask,request,Response,render_template,redirect
from crontab import CronTab
import couchdb,os,time

app = Flask(__name__)
cron = CronTab(user=True)
CHDB = os.environ['COUCHDB']
couch = couchdb.Server(CHDB)
try:
    db = couch['configurations']
except Exception as e:
    print("[{}] Configurations database does not exist, creating".format(time.mktime(time.gmtime())))
    couch.create('configurations')
    db = couch['configurations']
    print("[{}] Created configurations database".format(time.mktime(time.gmtime())))

if os.environ['ENV'] == 'dev':
    path = "/home/apottr/Programming/Python/raincloud-v2/"
    log = ">> {}activity.log 2>&1".format(path)
elif os.environ['ENV'] == 'prod':
    path = "/usr/"
    log = ">> /usr/src/activity.log 2>&1"

def gen_job_cmd(conf_id):
    typ = db[conf_id]['job_type']
    j = "{p}bin/python {p}jobs/{t}mod.py {c} {s} {e}".format(p=path,c=conf_id,s=CHDB,e=log,t=typ)
    return j


def add_job(conf_id,sched):
    job = cron.new(command=gen_job_cmd(conf_id))
    job.setall(sched)
    return job

def create_job(job):
    doc = db.save(job)
    jb = add_job(doc[0],job['schedule'])
    if jb.is_valid():
        cron.write()
        return doc[0]
    else:
        db.delete(db[doc[0]])
        cron.remove(jb)
        return False

def headers_str_to_obj(headers):
    out = {}
    h = [item.split(':') for item in headers.split('\n')]
    for line in h:
        out[line[0]] = line[1]
    return out

def form_to_conf(form):
    out = {}
    count = 0
    if form['schedule'] != '' and form['url'] != '':
        pass
    elif form['request.type'] != 'POST' and form['payload'] != '':
        pass
    else:
        return False

    out['request'] = {}
    out['request']['url'] = form['url']
    if form['headers'] != '':
        out['request']['headers'] = headers_str_to_obj(form['headers'])
    else:
        out['request']['headers'] = None
    if form['payload.type'] == 'json':
        out['request']['payload'] = json.loads(form['payload'])
    else:
        out['request']['payload'] = form['payload']
    out['request']['type'] = form['request.type']
    out['schedule'] = form['schedule']
    out['job_type'] = form['config.type']
    out['last'] = None

    return out

@app.route('/')
def index_route():
    lst = []
    for config in db.view('_all_docs',include_docs=True):
        print(config)
        last = config.doc['last'] if config.doc['last'] else '0_0'
        lst.append({
                'id': config.id,
                'url': config.doc['request']['url'],
                'last': last
            })
    return render_template('index.html',configs=lst)

@app.route('/details/<ident>')
def inspect_route(ident):
    cfg = db[ident]
    if not cfg['last']:
        last = {'contents': 'None'}
    else:
        last = couch['store_'+ident][cfg['last']]
    return render_template('job_info.html',config=cfg,last=last)

@app.route('/create', methods=['GET','POST'])
def create_job_route():
    try:
        error = ''
        if request.method == 'GET':
            return render_template('add_new.html')
        elif request.method == 'POST':
            conf = form_to_conf(request.form)
            jb = create_job(conf)
            return redirect('/')
    except Exception as e:
        print(e)
        print(request.form)
        return redirect('/')

@app.route('/delete', methods=['POST'])
def delete_job_route():
   ident = request.form['id']
   cron.remove_all(command=gen_job_cmd(ident))
   cron.write()
   db.delete(db[ident])
   del couch['store_{}'.format(ident)]
   return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
