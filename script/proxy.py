#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import json
import Queue
import requests
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(filename)s %(asctime)s %(thread)d [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_HTTPS_TEST_URL = 'https://www.baidu.com'
DEFAULT_HTTP_TEST_URL = 'http://www.csdn.net/'


class TooManyRetriesException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ProxyPool(object):
    def __init__(self, key='927200326076035', size=100, https=True, debug=False):
        self.https = https
        self.size = size
        self.key = key
        self.proxy_queue = Queue.Queue()
        self.proxy_queue_lock = threading.Lock()
        if debug:
            logger.setLevel(logging.DEBUG)

    # 代理可用测试
    def _proxy_test(self, proxy):
        if self.https:
            proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy,
            }
        else:
            proxies = {
                "http": "http://" + proxy,
            }

        url = DEFAULT_HTTPS_TEST_URL if self.https else DEFAULT_HTTP_TEST_URL
        try:
            content = requests.get(url, proxies=proxies, timeout=5).content
            if content:
                logger.debug('%s 代理可用' % str(proxy))
                self.proxy_queue.put(proxy)
                return True
            else:
                return False
        except Exception, e:
            logger.debug('%s 代理不可用,错误信息为: %s' % (str(proxy), str(e)))
        return False

    # 从接口获取代理列表
    def _acquire_proxy(self):
        logger.debug('刷新代理列表......')
        https_code = 2 if self.https else 1
        url = 'http://svip.kuaidaili.com/api/getproxy/?orderid=%s' \
              '&num=%d' \
              '&protocol=%d' \
              '&method=2&an_an=1&an_ha=1&format=json&sep=1&quality=2' % (self.key, self.size, https_code)
        try:
            res_json = json.loads(requests.get(url).content)
            if 'code' in res_json and res_json['code'] == 0:
                proxy_test_thread_list = []
                for proxy in res_json['data']['proxy_list']:
                    proxy_test_thread = threading.Thread(target=self._proxy_test, args=(proxy,))
                    proxy_test_thread.setDaemon(True)
                    proxy_test_thread.start()
                    proxy_test_thread_list.append(proxy_test_thread)

                for t in proxy_test_thread_list:
                    t.join()
        except Exception, e:
            logger.warn('获取代理列表失败,错误信息为:%s' % str(e))
        logger.debug('刷新代理列表完毕，当前代理数: %d' % self.proxy_queue.qsize())

    # 获取代理
    def _get_proxy(self):
        try_count = 0
        while True:
            try:
                proxy = self.proxy_queue.get(timeout=5)
                self.proxy_queue.task_done()
                return proxy
            except Queue.Empty, e:
                if self.proxy_queue_lock.acquire(1):
                    self._acquire_proxy()
                    try_count += 1
                    if try_count > 10:
                        logger.warn('无法获取代理，第%d次重试' % try_count)
                    self.proxy_queue_lock.release()

    # 请求
    def request(self, method, url, **kwargs):
        logger.debug('%s : %s' % (method, url))
        error_count = 0
        proxy_error_count = 0
        proxy = self._get_proxy()

        # 整个重试9次
        while error_count < 9:
            # 一个代理重试三次
            if proxy_error_count >= 3:
                proxy_error_count = 0
                proxy = self._get_proxy()

            proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy,
            }
            try:
                response = requests.request(method, url, proxies=proxies, timeout=5, **kwargs)
                self.proxy_queue.put(proxy)
                return response
            except Exception, e:
                error_count += 1
                proxy_error_count += 1
                logger.debug('%s : %s : %s 请求失败, 错误信息: %s, 第%d次重试' % (method, url, str(proxy), str(e), error_count))
        raise TooManyRetriesException('Too many retries')

    def get(self, url, params=None, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('get', url, params=params, **kwargs)

    def options(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('options', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('head', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request('post', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self.request('patch', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)