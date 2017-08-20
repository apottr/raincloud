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
    print("[{}] Configurations database does not exist, creating".format(time.gmtime()))
    couch.create('configurations')
    db = couch['configurations']
    print("[{}] Created configurations database".format(time.gmtime()))

if os.environ['ENV'] == 'dev':
    path = "/home/apottr/Programming/Python/raincloud-v2/"
    log = ">> {}activity.log 2>&1".format(path)
elif os.environ['ENV'] == 'prod':
    path = "/usr/"
    log = ">> /usr/src/activity.log 2>&1"

def gen_job_cmd(conf_id):
    typ = db[conf_id]['job_type']
    j = "{p}bin/python {p}src/jobs/{t}.py {c} {s} {e}".format(p=path,c=conf_id,s=CHDB,e=log,t=typ)
    return j


def add_job(conf_id,sched):
    job = cron.new(command=gen_job_cmd(conf_id))
    job.setall(sched)
    return job

def create_job(job):
    doc = db.save(job)
    jb = add_job(doc[0],job['schedule'])
    if jb.is_valid():
        return doc[0]
    else:
        db.delete(db[doc[0]])
        cron.remove(jb)
        return False

@app.route('/')
def index_route():
    lst = []
    for config in db.view('_all_docs',include_docs=True):
        print(config)
        lst.append({
                'id': config.id,
                'url': config.doc['request']['url'],
                'last': config.doc['last']
            })
    return render_template('index.html',configs=lst)

@app.route('/job/<ident>')
def inspect_route(ident):
    try:
        return db[ident]
    except:
        return "Not found"

@app.route('/create', methods=['GET','POST'])
def create_job_route():
    if request.method == 'GET':
        return render_template('add_new.html')
    elif request.method == 'POST':
        print(request.form)
        return redirect('/')

@app.route('/delete', methods=['GET','POST'])
def delete_job_route():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0")
