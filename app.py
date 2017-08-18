from flask import Flask,request,Response
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
    log = ">> {}src/activity.log 2>&1".format(path)

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
    pass

@app.route('/job/<ident>')
def inspect_route(ident):
    pass

@app.route('/create', methods=['GET','POST'])
def create_job_route():
    pass

@app.route('/delete', methods=['GET','POST'])
def delete_job_route():
    pass
