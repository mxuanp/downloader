#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import time
from apscheduler.schedulers.background import BackgroundScheduler

#select fiction from database, and check if there are new fictions
def update_new_fiction():
    print('new fiction')
#select all fictions from database, and update them
def update_all_fiction():
    print('update all fictions')
#update fictions
def update_fictions(fiction_list):
    print('update fictions')

#create a scheduled task, which runs once a minute
def start_minute_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_new_fiction, 'interval', seconds = 60)
    scheduler.start()

#create a scheduled task, which runs once a day
def start_day_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_new_fiction, 'cron', day_of_week = '0-6', hour=0, minute = 0, second = 0)
    scheduler.start()
#write log
def write_to_log(msg):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    pass
#set up two scheduled tasks
def start():
    start_minute_task()
    start_day_task()

if __name__ == '__main__':
    try:
        start()
        while True:
            time.sleep(86400)
    except:
        write_to_log()
