# -*- coding: utf-8 -*-
import requests
import re
import lxml.html
import pickle
import operator
import collections
from itertools import imap

import loadme


def save_file(_filename, _data):
    with open(_filename, 'w') as saveto:
        saveto.write(_data)

def append_file(_filename, _data):
    with open(_filename, 'a') as saveto:
        saveto.write(_data)

def get_last_page(pid, count):
    headers = {'User-Agent': 'Mozilla/5.0'}
    trg = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=' + str(pid) + \
        '&group_id=-1' + \
        '&user_id=-1' + \
        '&lang_id=-1' + \
        '&status_id=-1' + \
        '&statement_id=0' + \
        '&objectName=submits' + \
        '&count=' + str(count) + \
        '&with_comment=' + \
        '&page=-1' + \
        '&action=getPageCount'
    data = requests.get(trg, headers = headers)
    print data.text.split()
    return int(data.text.split()[2][:-2])

def get_json(pid, count, page):
    headers = {'User-Agent': 'Mozilla/5.0'}
    trg = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=' + str(pid) + \
        '&group_id=-1' + \
        '&user_id=-1' + \
        '&lang_id=-1' + \
        '&status_id=-1' + \
        '&statement_id=0' + \
        '&objectName=submits' + \
        '&count=' + str(count) + \
        '&with_comment=' + \
        '&page=' + str(page) + \
        '&action=getHTMLTable'
    data = requests.get(trg, headers = headers)
    return data.text

class Problem(object):
    def __init__(self, num, solver, label, timestamp, lang, status):
        self.num = num
        self.solver = solver
        self.label = label
        self.timestamp = timestamp
        self.lang = lang
        self.status = self.get_status(status)
    def __str__(self):
        return '# ' + str(self.num) + ' status: ' + self.status + ' date: ' + self.timestamp
    def get_status(self, status):
        if status == 'OK':
            return status
        elif status == 'Частичное решение':
            return 'partly'
        elif status == 'Ошибка компиляции':
            return 'ce'
        elif status == 'Неправильный ответ':
            return 'wrong'
        elif status == 'Ошибка во время выполнения программы':
            return 're'
        elif status == 'Превышено максимальное время работы':
            return 'limit'
        elif status == 'Неправильный формат вывода':
            return 'wo'
        else:
            return 'unk'


class MixParser(object):
    def __init__(self, _raw):
        super(MixParser, self).__init__()
        self.raw_data = _raw
    def clean(self):
        start =  self.raw_data.find('table')
        document = lxml.html.document_fromstring(self.raw_data[(start - 1):len(self.raw_data) - 3])
        return document.text_content()
    def encoding(self):

        spl = str(self.clean())
        spl = spl.replace('\\u', '^\\u')
        spl = spl.split('^') 
        for idx, item in enumerate(spl):
            if item.startswith('\\u'):
                spl[idx] = (item[0:6]).decode('unicode_escape').encode('utf-8') + item[6:]
        spl = ''.join(spl).replace('\\n\\n\\n', '\n').replace('\\n\\n', '\n').replace('\\n', '|').replace('\\', '')[1:]
        save_file('storage.txt', spl)
        return spl.split('\n')[2:]
    def parse(self):
        problems_info = list()
        data = self.encoding()
        for item in data[0:-1:3]:
            # print item
            if item[0] == '|':
                item = item[1:]
            data_str = item.split('|')
            problems_info.append(Problem(19, data_str[1], data_str[2].split('.')[1], data_str[3], data_str[4], data_str[5]))
            # print data_str
            # (self, num, solver, label, timestamp, lang, status):
            # print 'data_str[2]', data_str[2]
            # print type(data_str[2].split('.')[1])
            # pitem = Problem(19, data_str[1], data_str[2].split('.')[1], data_str[3], data_str[4], data_str[5])
            # print pitem.num
            # print pitem.label
            # print type(pitem.label)
            # print pitem.lang
        save_file('singel19.txt', '\n'.join(data[0].split('|')))
        return problems_info

#######
# get_last_page(18, 1)
# jx = get_last_page(18, 100)
# # print get_json(18, 2, 1)
# mp = MixParser(get_json(55, 10, 0))
# # mp.raw_data
# # mp.clean()
# # mp.encoding()
# problems = mp.parse()
# for p in problems:
#     print p
#######

def get_url(pid, count, page):
    trg = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=' + str(pid) + \
        '&group_id=-1' + \
        '&user_id=-1' + \
        '&lang_id=-1' + \
        '&status_id=-1' + \
        '&statement_id=0' + \
        '&objectName=submits' + \
        '&count=' + str(count) + \
        '&with_comment=' + \
        '&page=' + str(page) + \
        '&action=getHTMLTable'
    return trg


def collect_data(pid):
    urlrange = list()
    for i in xrange(get_last_page(pid, 100)):
        urlrange.append(get_url(pid, 100, i))

    storage = list()
    for r in loadme.load(urlrange, 20):
        mp = MixParser(r)
        problems = mp.parse()
        storage += problems
    # for p in storage:
    #     print p
    storage.sort(key=operator.attrgetter('timestamp'))
    print len(storage)
    with open('basedata', 'wb') as f:
        pickle.dump(storage[0:40], f)
    return storage[1:120]

    # ###

def add_data(pid):
    with open('basedata','rb') as f:
        storage = pickle.load(f)
    base = len(storage)
    new = get_last_page(pid, 1)
    diff = (new - base) / 100 + int(bool((new - base) % 100))
    print 'diff', diff
    base_range_len = (base) / 100 + int(bool((base) % 100))
    urlrange = list()
    frange = range(base_range_len + diff - 1)[:diff]
    for i in frange:
        urlrange.append(get_url(pid, 100, i))
    nstorage = list()
    for i in urlrange:
        mp = MixParser(get_json(pid, 100, i))
        problems = mp.parse()
        nstorage += problems
    nstorage.sort(key=operator.attrgetter('timestamp'))
    print 'pr len:', len(nstorage)
    for i, el in enumerate(nstorage):
        if el.timestamp == storage[-1].timestamp:
            print i
            border = i
    # print nstorage[border+1:]
    return storage + nstorage[border+1:]

    # return nstorage

