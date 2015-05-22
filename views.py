# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
# from django.utils import timezone
# import pytz

from collections import OrderedDict
import operator
import os
import datetime
from itertools import chain
import loadme
import statsloaderx

# from django.db import models
from mccme.models import Problem, UserProfile, UserProblems
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#from pre_test import *

class ProblemByUser(object):
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

def test(request):
    return HttpResponse('Hello World')

def action(request):
#    return HttpResponse(request.body)

    urlrangex = list()

    with open(os.path.join('/home/django/django_project/mccme','plist.txt'), 'r') as plist:
        content = plist.readlines()

    def get_last_page_url(pid):
        trg = 'http://informatics.mccme.ru/moodle/ajax/ajax.php?problem_id=' + str(pid) + \
            '&group_id=-1' + \
            '&user_id=-1' + \
            '&lang_id=-1' + \
            '&status_id=-1' + \
            '&statement_id=0' + \
            '&objectName=submits' + \
            '&count=1' + \
            '&with_comment=' + \
            '&page=-1' + \
            '&action=getPageCount'
        return trg

    content = map(str.strip, content)
    for el in content:
        urlrangex.append(get_last_page_url(el))
    stats = dict()
    for r in loadme.load(urlrangex, 75):
        stats[int(r[1])] = int(r[0].split()[2][:-2])

    problems_in_db = Problem.objects.all()
    for pid, submits in stats.iteritems():
        problems= problems_in_db.filter(pid=pid)
        if problems:
            if problems[0].submits != submits:
                problems[0].submits = submits
                problems[0].save()
        else:
            # problem = Problem(pid=pid, submits=submits)
            problem = Problem()
            problem.pid = pid
            problem.submits = submits
            problem.save()


#    print r
#print stats # problem : attempts
##    with open('byproblem.txt', 'w') as bp:
  ##      for k, v in collections.OrderedDict(sorted(stats.iteritems())).iteritems():
#        print str(k) + '\t' + str(v)
    ##        bp.write(str(k) + '\t' + str(v) + '\n')

# ss = sorted(stats.items(), key=operator.itemgetter(1))
# print ss

##    with open('bysolutions.txt', 'w') as bs:
  ##      for k, v in sorted(stats.items(), key=operator.itemgetter(1)):
#        print str(k) + '\t' + str(v)
    ##        bs.write(str(k) + '\t' + str(v) + '\n')

    return HttpResponse(str(stats))

def show_me(request):
    return render(request, 'mccme/problems.html', {
        'problems': sorted(Problem.objects.all(), key=operator.attrgetter('submits'), reverse=True)
        })

def user_stats(request, uid):
    data_stats = statsloaderx.get_user_success_info(int(uid), 75, 100)
    solved = map(int, data_stats[0])
    unsolved = map(int, data_stats[1])
    users_in_db = UserProfile.objects.all()
    cuser = users_in_db.filter(uid=uid)
    if cuser:
        # cu.solved_problems.all().delete
        cuser = cuser[0]
        cuser.solved_problems.clear()
        cuser.unsolved_problems.clear()
        for ep in solved:
            cproblem = Problem.objects.all().filter(pid=ep)[0]
            cuser.solved_problems.add(cproblem)
        for ep in unsolved:
            cproblem = Problem.objects.all().filter(pid=ep)[0]
            cuser.unsolved_problems.add(cproblem)
        cuser.save()
    else:
        cuser = UserProfile(uid=uid)
        cuser.save()
        for ep in solved:
            cproblem = Problem.objects.all().filter(pid=ep)[0]
            cuser.solved_problems.add(cproblem)
        for ep in unsolved:
            cproblem = Problem.objects.all().filter(pid=ep)[0]
            cuser.unsolved_problems.add(cproblem)
        # cuser.save()
        # cuser = UserProfile(uid=uid, solved_problems=data_stats[0], unsolved_problems=data_stats[1])
        cuser.save()
    # return HttpResponse('user_stats: ' + uid + '\nsuccess: ' + str(data_stats[0]))
    # return HttpResponse('user_stats: ' + uid + '\nsuccess: ' + str(cuser.solved_problems.all()) + '\n' + str(cuser.unsolved_problems.all()))
    return render(request, 'mccme/userinfo.html',
                  {'problems_solved': cuser.solved_problems.all(),
                   'problems_unsolved': cuser.unsolved_problems.all()
                   })

def show_user(request, uid):
    data_stats = statsloaderx.get_user_success_info(int(uid), 75, 100)
    solved = map(int, data_stats[0])
    unsolved = map(int, data_stats[1])
    users_in_db = UserProfile.objects.all()
    cuser = users_in_db.filter(uid=uid)
    if cuser:
        cuser = cuser[0]
        cuser.solved_problems.clear()
        cuser.unsolved_problems.clear()
        for ep in solved:
            cuser.solved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        for ep in unsolved:
            cuser.unsolved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        cuser.save()
    else:
        cuser = UserProfile(uid=uid)
        cuser.save()
        for ep in solved:
            cuser.solved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        for ep in unsolved:
            cuser.unsolved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        cuser.save()
    all_problems = {problem: 'unsolved' for problem in Problem.objects.all()}
    for problem in cuser.solved_problems.all():
        if problem in all_problems.keys():
            all_problems[problem] = 'solved'
    for problem in cuser.unsolved_problems.all():
        if problem in all_problems.keys():
            all_problems[problem] = 'in_progress'
    all_problems = OrderedDict(sorted(all_problems.items(), key=lambda x: x[0].submits, reverse=True))
    total_count = len(all_problems.keys())
    solved_count = len(cuser.solved_problems.all())
    trying_count = len(cuser.unsolved_problems.all())
    submitted_by_smb = len([1 for p in Problem.objects.all() if p.submits > 0])
    return render(request, 'mccme/user_progress.html', {
                        'user': uid, 
                        'problems': all_problems,
                        'solved_count': solved_count,
                        'total_count': total_count,
                        'trying_count': trying_count,
                        'progress': '{0:.4f}'.format(float(solved_count)/total_count * 100),
                        'progress_light': '{0:.4f}'.format(float(solved_count)/submitted_by_smb * 100)
                        })

def multi_stats(request, uid):
    page = int(request.GET.get('page'))
    count = 50
    # page = 1
    # return HttpResponse(str(uid) + ' - ' + str(page))
    # tp = get_last_page(_uid, 1)
    total_count = statsloaderx.get_last_page(uid, 1)
    # data_stats = statsloaderx.get_user_success_info(int(uid), 75, 100)
    # solved = map(int, data_stats[0])
    # unsolved = map(int, data_stats[1])
    # total_count = data_stats[2]
    users_in_db = UserProfile.objects.all()
    cuser = users_in_db.filter(uid=uid)
    if cuser:
        cuser = cuser[0]
        if cuser.tcount != total_count:
            data_stats = statsloaderx.get_user_success_info(int(uid), 75, 100)
            solved = map(int, data_stats[0])
            unsolved = map(int, data_stats[1])
            cuser.solved_problems.clear()
            cuser.unsolved_problems.clear()
            for ep in solved:
                cuser.solved_problems.add(Problem.objects.all().filter(pid=ep)[0])
            for ep in unsolved:
                cuser.unsolved_problems.add(Problem.objects.all().filter(pid=ep)[0])
            cuser.save()
    else:
        data_stats = statsloaderx.get_user_success_info(int(uid), 75, 100)
        solved = map(int, data_stats[0])
        unsolved = map(int, data_stats[1])
        cuser = UserProfile(uid=uid, tcount=total_count)
        cuser.save()
        for ep in solved:
            cuser.solved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        for ep in unsolved:
            cuser.unsolved_problems.add(Problem.objects.all().filter(pid=ep)[0])
        cuser.save()
    # all_problems = {problem: 'unsolved' for problem in Problem.objects.all()}
    # for problem in cuser.solved_problems.all():
    #     if problem in all_problems.keys():
    #         all_problems[problem] = 'solved'
    # for problem in cuser.unsolved_problems.all():
    #     if problem in all_problems.keys():
    #         all_problems[problem] = 'in_progress'
    # all_problems = OrderedDict(sorted(all_problems.items(), key=lambda x: x[0].submits, reverse=True))
    # dtotal_count = len(all_problems.keys())
    dtotal_count = len(Problem.objects.all())
    solved_count = len(cuser.solved_problems.all())
    trying_count = len(cuser.unsolved_problems.all())
    submitted_by_smb = len([1 for p in Problem.objects.all() if p.submits > 0])

    paginator = Paginator(sorted(Problem.objects.all(), key=operator.attrgetter('submits'), reverse=True), 50)
    try:
        pproblems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pproblems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pproblems = paginator.page(paginator.num_pages)
    return render(request, 'mccme/user_progress_ru.html', {
                        'user': uid,
                        # 'problems': all_problems[((int(page)-1) * 100):(int(page) * 100)],
                        # 'problems': {k: all_problems[k] for k in all_problems.keys()[((int(page)-1) * 100):(int(page) * 100)]},
                        # OrderedDict(xspamher.items()[1:3])
                        'problems_solved': cuser.solved_problems.all(),
                        'problems_unsolved': cuser.unsolved_problems.all(),
                        # 'problems': OrderedDict(all_problems.items()[((int(page)-1) * count):(int(page) * count)]),

                        # 'problems': sorted(Problem.objects.all(), key=operator.attrgetter('submits'), reverse=True)[((int(page)-1) * count):(int(page) * count)],
                        'problems': pproblems,
                        'total_list': list(chain(cuser.solved_problems.all(), cuser.unsolved_problems.all())),
                        # 'pages': xrange(1, dtotal_count / 50 + 2),
                        # {k: bigdict[k] for k in ('l', 'm', 'n')}
                        'solved_count': solved_count,
                        'total_count': dtotal_count,
                        'trying_count': trying_count,
                        'progress': '{0:.4f}'.format(float(solved_count)/dtotal_count * 100),
                        'progress_light': '{0:.4f}'.format(float(solved_count)/submitted_by_smb * 100)
                        })


def ex_users(request):
    users = UserProfile.objects.all()
    for user in users:
        user.uname = statsloaderx.get_user_name(user.uid)
        user.save()

    return render(request, 'mccme/users_ru.html', {
                  'users': users
                    })

def success_stats(request, uid):
    # utc = pytz.UTC
    # now = utc.localize(datetime.datetime.now())
    # now = timezone.now()
    # timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    sproblems = statsloaderx.collect_user_total_success(uid, 75, 100)
    bproblems = UserProblems.objects.all().filter(uid=uid)
    timelist = [p.timestamp.strftime("%Y-%m-%d %H:%M:%S") for p in bproblems]
    # timelist = [utc.localize(p.timestamp) for p in bproblems]
    for p in sproblems:
        if p.timestamp not in timelist:
        # if utc.localize(datetime.datetime.strptime(p.timestamp, "%Y-%m-%d %H:%M:%S")) not in timelist:
            cpromlem = UserProblems(uid=uid, plabel=p.label, timestamp=p.timestamp)
            cpromlem.save()
    # UserProblems.objects.all().filter(uid=uid))
    # return HttpResponse('test -> ' + str(uid) + '\n' + str(UserProblems.objects.all().filter(uid=uid)))
    return render(request, 'mccme/user_success.html', {
                  'success_problems': UserProblems.objects.all().filter(uid=uid)
                 })