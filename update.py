#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import time
import os
import configparser 
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
import conf
#select fiction from database, and check if there are new fictions
def update_new_fictions():
    cf = configparser.ConfigParser()
    cf.read("config.conf")
    options = cf.options('fiction')
    last_fiction = cf.getint('fiction', options[0])
    fiction_list = []
    db, cursor = get_db()
    sql = "select num,updating,currenturl from fiction where id > %s order by id";
    cursor.execute(sql, last_fiction)
    results = cursor.fetchall()
    for row in results:
        fiction_list.append(row)
    close_db()
    update_fictions(fiction_list)
#select all fictions from database, and update them
def update_all_fictions():
    print('update all fictions')
    fiction_list = []
    db, cursor = get_db()
    sql = "select num,updating,currenturl from fiction";
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        fiction_list.append(row)
    close_db()
    update_fictions(fiction_list)
#update fictions
def update_fictions(fiction_list):
    print(str(fiction_list))

#get a database connection
def get_db():
    db = pymysql.connect(conf.mysql_host, conf.mysql_user, conf.mysql_password, conf.mysql_db)
    cursor = db.cursor()
    return db,cursor
#close database connection
def close_db(db,cursor):
    cursor.close()
    db.close()

#create a scheduled task, which runs once a minute
def start_minute_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_new_fiction, 'interval', seconds = 60)
    scheduler.start()

#create a scheduled task, which runs once a day
def start_day_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_all_fictions, 'cron', day_of_week = '0-6', hour=0, minute = 0, second = 0)
    scheduler.start()
#write log
def write_to_log(msg):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_str = current_time + msg + '\n'
    with open(conf.log_file, mode = 'a') as logs:
        logs.write(log_str)
#set up two scheduled tasks
def start():
    start_minute_task()
    start_day_task()

if __name__ == '__main__':
    update_new_fictions()
    '''
    try:
        start()
        while True:
            write_to_log(' INFO system is normal')
            time.sleep(86400)
    except Exception as e:
        write_to_log(' ERROR '+str(e))
    '''
