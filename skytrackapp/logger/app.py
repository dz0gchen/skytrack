# coding: UTF-8

import redis
import datetime
from flask import render_template
from collections import OrderedDict
from flask import Flask, request as flask_req
from wtforms import Form, TextField, IntegerField, validators

cache = redis.StrictRedis(host="localhost", port=6379, db=0)
app = Flask(__name__)

class Form(Form):
    login = TextField('Login', [validators.Length(min=3, max=30), validators.InputRequired()])
    action = TextField('Action', [validators.Length(min=3, max=512), validators.InputRequired()])
    eltime = IntegerField('Elapsed time', [validators.NumberRange(min=1, max=999), validators.InputRequired()])
    
@app.template_filter('getListVal')
def getListVal(st):
    li = eval(st)
    return li[0], li[1], li[2]
     
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = Form(flask_req.form)
    #cache.flushall()
    if flask_req.method == 'POST' and form.validate():
        
        cache.lpush(form.login.data, [form.action.data, form.eltime.data, datetime.date.today().strftime("%Y-%m-%d")])
                 
        cache.lpush('last', [form.login.data, form.action.data, form.eltime.data])
        if len(cache.lrange('last', 0, 22)) > 20:
            cache.rpop('last')
                                             
    return render_template('index.html', title = 'Index', form=form, last_entries=cache.lrange('last', 0, 20))

@app.route('/report', methods=['GET'])
def report():
 
    daysmap = OrderedDict([(6,u'Вс'),(5,u'Сб'),(4,u'Пт'),(3,u'Чт'),(2,u'Ср'),(1,u'Вт'),(0,u'Пн')])

    now_date = datetime.date.today()  
    now_day = now_date.weekday()
    
    ind = daysmap.keys()
    daysorder = OrderedDict()
    for i, el in enumerate(ind[ind.index(now_day):]+ind[:ind.index(now_day)]):
        delta = datetime.timedelta(days=i)
        daysorder[daysmap[el]] = (now_date - delta).strftime("%Y-%m-%d")
    
    report = {}
       
    for login in cache.keys():
        if login == 'last':
            continue
        
        report[login] = {}
        for userdata in cache.lrange(login, 0, -1):
            userdata = eval(userdata)
            
            if userdata[2] not in daysorder.values():
                break
            
            hours = round(userdata[1] / 60.0, 2)
           
            if report[login].get(userdata[2]):
                report[login][userdata[2]] = report[login][userdata[2]] + hours
            else:    
                report[login][userdata[2]] = hours
                                                  
    return render_template('report.html', title = 'Report', daysorder=daysorder, report=report)

if __name__ == '__main__':
    app.run()

