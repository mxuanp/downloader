# -*- coding: utf-8 -*-
#!/usr/bin/python3
#@author xuan
#@created 2019/10/28
#@desciption global utils 

import logging

#配置logging对象
def get_logger(log_file,logging_name):
    logger = logging.getLogger(logging_name)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler(log_file,encoding = 'UTF-8')
    handler.setLevel(logging.INFO)
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formater)
    logger.addHandler(handler)
    return logger
