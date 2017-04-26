#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib


def md5(string):
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest().upper()
