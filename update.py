# -*- coding: utf-8 -*-
#!/usr/bin/python3
#@author xuan
#@created 2019/10/19
#@desciption Complete tasks at regular intervals

#system lib
import time
import os
import configparser 
import logging
import MySQLdb
from apscheduler.schedulers.background import BackgroundScheduler
from DBUtils.PooledDB import PooledDB
#my lib
from downloader import downloader
import conf
import utils


#配置数据库连接池
db_connectoin_pool = PooledDB(MySQLdb, 5, host=conf.mysql_host, user = conf.mysql_user, passwd = conf.mysql_password, db = conf.mysql_db, port = 3306)

logger = utils.get_logger(log_file = conf.update_log_file, logging_name = 'update_logger')
#get a database connection
def get_db():
    db = db_connectoin_pool.connection()
    #db = pymysql.connect(conf.mysql_host, conf.mysql_user, conf.mysql_password, conf.mysql_db)
    cursor = db.cursor()
    return db,cursor
#close database connection
def close_db(db,cursor):
    cursor.close()
    db.close()

#下载或更新小说
def update_fictions(fiction_list):
    for fiction in fiction_list:
        #print(fiction)
        path = conf.fiction_dir + str(fiction[0])
        try:
            #存放该小说的文件夹，如果没有新建
            os.mkdir(path)
        except FileExistsError:
            pass
        db, cursor = get_db()
        try:
            #更新小说状态，以免其它任务重复下载
            sql = 'update fiction set updating = 1 where id = %s'
            db, cursor = get_db()
            cursor.execute(sql, (str(fiction[0])))
            db.commit()
        except Exception as e:
            logger.error("database error, and rollback", exc_info = True)
            db.rollback()
        close_db(db, cursor)
        logger.info("downloading fiction id:"+str(fiction[0])+",url:"+fiction[1])
        dl = downloader(url = fiction[1], num = fiction[2], path = path, fiction_id = fiction[0])
        num = dl.update()
        try:
            sql = 'update fiction set num = %s,updating=0 where id = %s'
            db, cursor = get_db()
            cursor.execute(sql, (num, fiction[0]))
            db.commit()
        except Exception as e:
            logger.error("database error, and rollback", exc_info = True)
            db.rollback()
        close_db(db, cursor)

#更新新增加的小说
def update_new_fictions():
    #获取配置文件
    cf = configparser.ConfigParser()
    cf.read("config.conf")
    options = cf.options('fiction')
    #读取上次更新的小说的id
    last_fiction = cf.getint('fiction', options[0])
    fiction_list = []
    db, cursor = get_db()
    sql = "select id,url,num,updating from fiction where id > %s order by id";
    cursor.execute(sql, str(last_fiction))
    results = cursor.fetchall()
    last_fiction_id = last_fiction
    for row in results:
        if row[3] == 0:
            fiction_list.append(row)
            last_fiction_id = row[0]
    #把新增加的小说的最后一本的id写入配置文件，方便下次更新查询
    cf.set('fiction', options[0], str(last_fiction_id))
    with open('config.conf','w') as f:
        cf.write(f)
    logger.info('update new fictions')
    #关闭数据库连接
    close_db(db, cursor)
    #下载小说
    update_fictions(fiction_list)

#更新数据库中的所有小说
def update_all_fictions():
    fiction_list = []
    db, cursor = get_db()
    sql = "select id,url,num,updating from fiction";
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        if row[3] == 0:
            fiction_list.append(row)
    logger.info("update all fictions")
    #关闭数据库连接
    close_db(db, cursor)
    #下载小说
    update_fictions(fiction_list)

#create a scheduled task, which runs once a minute
def start_minute_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_new_fictions, 'interval', seconds = 60)
    scheduler.start()

#create a scheduled task, which runs once a day
def start_day_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_all_fictions, 'cron', day_of_week = '0-6', hour=0, minute = 0, second = 0)
    scheduler.start()
#set up two scheduled tasks
def start():
    start_minute_task()
    start_day_task()

if __name__ == '__main__':
    try:
        start()
        while True:
            logger = utils.get_logger(log_file = conf.update_log_file, logging_name = 'update_logger')
            logger.info("system is normal")
            time.sleep(86400)
    except Exception as e:
        logger = utils.get_logger(log_file = conf.update_log_file, logging_name = 'update_logger')
        logger.error("system error", exc_info = True)
