# coding: UTF-8

#sudo apt-get update
#sudo apt-get install sqlite3 libsqlite3-dev
#sudo ./pip install pysqlite

#EDITOR=gedit crontab -e
#*/1 * * * * /opt/zvooq/bin/python /home/user/workspace/skytrack/skytrackapp/logger/importdata.py >> /tmp/out.txt 2>&1

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Logins, UserData

import redis
cache = redis.StrictRedis(host="localhost", port=6379, db=0)

engine = create_engine('sqlite:////tmp/test.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
session = DBSession()

#очищаем таблицу перед загузкой данных
session.query(Logins).delete()
session.query(UserData).delete()

for login in cache.keys():
    if login == 'last':
        continue
    
    loginobj = Logins(logins=login)
    session.add(loginobj)
    #сбрасываем изменения в базу 
    session.flush()
    #обновляем объект
    session.refresh(loginobj)
        
    for userdata in cache.lrange(login, 0, -1):
        userdata = eval(userdata)
        userdata = UserData(login_id = loginobj.id, 
                            action = userdata[0], 
                            eltime = userdata[1], 
                            time = userdata[2])
        
        session.add(userdata)
                            
session.commit()

#простой inner join
query = session.query(UserData, Logins).filter(UserData.login_id == Logins.id)
records = query.all()

for userdata, logins in records:
    print (logins.logins, userdata.action, userdata.eltime, userdata.time)

session.close_all()

 
