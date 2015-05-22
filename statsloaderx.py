# -*- coding: utf-8 -*-

import requests
import lxml.html
import re
import operator


import loadme

def get_last_page(_id, _pc):
    target_url = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=0' + \
        '&objectName=submits' + \
        '&group_id=0' + \
        '&user_id=' + str(_id) + \
        '&status_id=-1' + \
        '&lang_id=-1' + \
        '&count=' + str(_pc) + \
        '&with_comment=' + \
        '&statement_id=0' + \
        '&action=getPageCount'
    data = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'})
    return int(re.findall(r'\d+', str(data.text))[0])

def get_url_range(_id, _pc):
    url_range = []
    for page in xrange(get_last_page(_id, _pc)):
        target_url = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=0' + \
            '&group_id=0' + \
            '&user_id=' + str(_id) + \
            '&lang_id=-1' + \
            '&status_id=-1' + \
            '&statement_id=0' + \
            '&objectName=submits' + \
            '&count=' + str(_pc) + \
            '&with_comment=' + \
            '&page=' + str(page) + \
            '&action=getHTMLTable'
        url_range.append(target_url)
    return url_range

def save_file(_filename, _data):
    with open(_filename, 'a') as saveto:
        saveto.write(_data)

def save_filex(_filename, _data):
    with open(_filename, 'w') as saveto:
        saveto.write(_data)


class Problem(object):
    def __init__(self, num, solver, label, timestamp, lang, status):
        self.num = num
        self.solver = solver
        self.label = label
        self.timestamp = timestamp
        self.lang = lang
        self.status = self.get_status(status)
    def __str__(self):
        return '# ' + str(self.num) + '|' + \
                ' label:' + str(self.label) + '|' + \
                ' status: ' + self.status + '|' + \
                ' date: ' + self.timestamp
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
        spl = str(self.clean().encode('utf8'))
        spl = spl.replace('\\u', '^\\u')
        spl = spl.split('^') 
        for idx, item in enumerate(spl):
            if item.startswith('\\u'):
                spl[idx] = (item[0:6]).decode('unicode_escape').encode('utf-8') + item[6:]
        spl = ''.join(spl).replace('\\n\\n\\n', '\n').replace('\\n\\n', '\n').replace('\\n', '|').replace('\\', '')[1:]
        save_filex('storage2.txt', spl)
        return spl
    def encoding_e(self, suff):
        spl = str(self.clean())
        spl = spl.replace('\\u', '^\\u')
        spl = spl.split('^')
        xgrb = list() 
        for idx, item in enumerate(spl):
            if item.startswith('\\u'):
                xgrb.append(item)
                # spl[idx] = (item[0:6]).decode('unicode_escape').encode('utf-8') + item[6:]
        # spl = ''.join(spl).replace('\\n\\n\\n', '\n').replace('\\n\\n', '\n').replace('\\n', '|').replace('\\', '')[1:]
        save_file('storage_errs' + suff + '.txt', ' '.join(xgrb))
    def parse(self):
        problems_info = list()
        try:
            data = self.encoding().split('\n')[2:]
        except Exception, e:
            print e
            # print e.__str__().split()[8][:-1]
            return 'na'
        for i in xrange(len(data) - 1):
            if data[i].startswith('|'):
                data[i] = data[i][1:]
            if '-' in data[i].split('|')[0] and len(data[i].split('|')) > 2:
                data_str = data[i].split('|')
                if data_str[2].split('.')[0]:
                    num = data_str[2].split('.')[0]  
                if data_str[2].split('.')[1]:
                    label = data_str[2].split('.')[1]
                else:
                    label = 'no name'
                if len(data_str) < 6:
                    status = data[i+1]
                else:
                    status = data_str[5]
                try:
                    lang = data_str[4]
                except Exception, e:
                    lang = 'n/a'
                try:
                    timestamp = data_str[3]
                except Exception, e:
                    timestamp = 'n/a'
                try:
                    solver = data_str[1]
                except Exception, e:
                    solver = 'n/a'
                problems_info.append(Problem(num, solver, label, timestamp, lang, status))
        return problems_info

def collect_user_info(_uid, _num_threads, _pc):
    tp = get_last_page(_uid, 1)
    print 'total problems:', tp
    result_pages = [el[0] for el in loadme.load(get_url_range(_uid, _pc), _num_threads)]
    user_submits = sorted([item for subl in [MixParser(page).parse() for page in result_pages] for item in subl], key=operator.attrgetter('timestamp'))
    print len([p for p in user_submits if p.status == 'OK'])
    print len(user_submits)
    print len(unique_problems(user_submits))
    ds = get_dict_stats(user_submits)
    print ds
    print len([pn for pn in ds.keys() if not ds[pn][1]])
    print unique_problems(user_submits)
    with open( '__' + str(_uid) + 's.txt', 'w') as outm:
        outm.write(str(tp) + ': '  + str(len(user_submits)) + '\n')
        # for p in user_submits:
        for p in unique_problems(user_submits):
          outm.write(str(p) + '\n')
    return user_submits

def unq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def problems_by_num(_num, _plist):
    return [p for p in _plist if p.num == _num][0]


def unique_problems(_plist):
    tmp = [p for p in _plist if p.status == 'OK']

    nums = unq([p.num for p in tmp])
    return [problems_by_num(n, tmp) for n in nums]

def get_dict_stats(_plist):
    parsedl = [(p.num, p.status) for p in _plist]
    pdict = dict()
    for item in parsedl:
        if item[0] not in pdict.keys():
            pdict[item[0]] = list()
        pdict[item[0]].append(item[1])
    sdict = {}
    for k, v in pdict.iteritems():
        sdict[k] = len(v), True if 'OK' in v else False
    return sdict
    # return [(p.num, p.status) for p in _plist]

def get_user_name(_id):
    url_range = []
    target_url = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=0' + \
        '&group_id=0' + \
        '&user_id=' + str(_id) + \
        '&lang_id=-1' + \
        '&status_id=-1' + \
        '&statement_id=0' + \
        '&objectName=submits' + \
        '&count=1' + \
        '&with_comment=' + \
        '&page=0' + \
        '&action=getHTMLTable'
    data = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'})
    # return int(re.findall(r'\d+', str(data.text))[0])
    return MixParser(data.text).parse()[0].solver

def get_user_success_info(_uid, _num_threads, _pc):
    tp = get_last_page(_uid, 1)
    # print 'total problems:', tp
    result_pages = [el[0] for el in loadme.load(get_url_range(_uid, _pc), _num_threads)]
    user_submits = sorted([item for subl in [MixParser(page).parse() for page in result_pages] for item in subl], key=operator.attrgetter('timestamp'))
    print len(user_submits)
    ds = get_dict_stats(user_submits)
    solved = [pn for pn in ds.keys() if ds[pn][1]]
    in_progress = [pn for pn in ds.keys() if not ds[pn][1]]
    # print solved
    # print in_progress
    return solved, in_progress, tp

def collect_user_total_success(_uid, _num_threads, _pc):
    tp = get_last_page(_uid, 1)
    # print 'total problems:', tp
    result_pages = [el[0] for el in loadme.load(get_url_range(_uid, _pc), _num_threads)]
    user_submits = sorted([item for subl in [MixParser(page).parse() for page in result_pages] for item in subl], key=operator.attrgetter('timestamp'))
    # print len([p for p in user_submits if p.status == 'OK'])
    # print len(user_submits)
    # with open( '__' + str(_uid) + 's.txt', 'w') as outm:
        # outm.write(str(tp) + ': '  + str(len([p for p in user_submits if p.status == 'OK'])) + '\n')
        # for p in [p for p in user_submits if p.status == 'OK']:
          # outm.write(str(p) + '\n')
    return [p for p in user_submits if p.status == 'OK']


# for u in xrange(100, 200):
#     collect_user_info(u, 75, 100)
# collect_user_info(11083, 75, 100)
# collect_user_info(99669, 75, 100)
#print get_user_success_info(99669, 75, 100)
# collect_user_info(8732, 75, 100)
# collect_user_info(8732, 75, 100)

# print get_user_name(99669)

print collect_user_total_success(11083, 75, 100)
#####################
