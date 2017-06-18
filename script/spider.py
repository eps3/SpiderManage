#!/usr/bin/env python
# -*- coding:utf-8 -*-
import MySQLdb
import json
import hashlib
import redis
import re
import traceback
import time
import thread
import logging

# import multiprocessing as mul

THREAD_COUNT = 10
# Redis Config
REDIS_HOST = '120.25.227.8'
REDIS_PORT = 6379
REDIS_PASSWORD = 'xuxinredis'

MYSQL_HOST = '120.25.227.8'
MYSQL_USER = 'root'
MYSQL_PWD = 'xuxin.mysql'
MYSQL_DB = 'spider_db'
PROJECT_NAME = 'spider_manage'

RELOAD_TIME = 5
TASK_LIST = []

logging.basicConfig(level=logging.INFO,
                    format='%(filename)s %(asctime)s %(thread)d [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def md5(string):
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()


def manage():
    logger.info('启动爬虫节点...')
    db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, MYSQL_DB)
    while True:
        logger.info('获取任务列表...')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM tasks;')
        tasks = cursor.fetchall()
        for task in tasks:
            # task_id = task[0]
            task_name = task[1]
            user_id = task[2]
            json_info = task[3]
            status = task[4]
            if task_name in TASK_LIST:
                # 移出不存在的任务
                if status != 0:
                    logger.info('任务%s的状态为%d,移出该任务' % (task_name, status))
                    TASK_LIST.remove(task_name)
                # 如果已经存在则跳过
                continue
            if status != 0:
                # 如果不是启动状态则跳过
                continue

            json_config = json.loads(json_info)
            # process_count = json_info.get('PROCESS_COUNT', 1)
            thread_count = json_config.get('THREAD_COUNT', 10)
            logger.info('启动任务%s，来自用户%d, 配置信息为: %s' % (task_name, user_id, json_info))
            TASK_LIST.append(task_name)
            for i in range(0, thread_count):
                thread.start_new_thread(thread_task, (task_name, user_id, json_config))
        time.sleep(RELOAD_TIME)


def thread_task(task_name, user_id, json_config):
    queue = '.'.join([md5(PROJECT_NAME), str(user_id), md5(task_name)])
    redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    try:
        if task_name not in TASK_LIST:
            return
        logger.info('开始监听任务%s,队列key为%s' % (task_name, queue))
        while True:
            task = redis_db.blpop(queue + '.TASK', timeout=2)
            if not task:
                if task_name in TASK_LIST:
                    logger.info('task: %s,queue: %s time out' % (task_name, queue))
                    continue
                else:
                    break
            url = task[1]
            try:
                # 判断是否使用代理
                if json_config.get('USE_PROXY', 0) == 0:
                    from proxy import ProxyPool
                    requests = ProxyPool(key='927200326076035', debug=True)
                else:
                    import requests
                # 判断是否使用随机请求头
                if json_config.get('RANDOM_AU', 0) == 0:
                    # print 'RANDOM AU'
                    pass
                resp = requests.get(url)
                logger.info('GET %s' % url)
                task_res = {}
                # 解析结果内容
                for res in json_config.get('RESULT', []):
                    key = res[0]
                    rex = res[1]
                    if rex == 'ALL':
                        value = resp.content
                    else:
                        value = re.findall(rex, resp.content)[0]
                    task_res[key] = value
                # 解析下一个url
                for task_rex in json_config.get('TASK_REX', []):
                    next_urls = re.findall(task_rex, resp.content)
                    for next_url in next_urls:
                        # 判断是否已经存在该任务
                        if redis_db.sismember(queue + '.ALL', next_url):
                            continue
                        redis_db.lpush(queue + '.ALL', next_url)
                        redis_db.lpush(queue + '.TASK', next_url)
                # 将结果存入结果队列
                logger.info('OK %s' % url)
                redis_db.lpush(queue + '.OK', url)
                redis_db.lpush(queue + '.RESULT', json.dumps(task_res))
            except Exception, e:
                logger.info('ERR %s %s' % (url, str(e)))
                # 将错误存入错误队列
                error_msg = {
                    'task_name': task_name,
                    'url': url,
                    'simple_msg': str(e),
                    'more_msg': traceback.format_exc()
                }
                redis_db.lpush(queue + '.ERROR', json.dumps(error_msg))
    except Exception, e:
        logger.info('任务出现错误 %s %s' % (task_name, str(e)))
        # 将错误存入错误队列
        error_msg = {
            'task_name': task_name,
            'simple_msg': str(e),
            'more_msg': traceback.format_exc()
        }
        redis_db.lpush(queue + '.ERROR', json.dumps(error_msg))


if __name__ == '__main__':
    manage()
