from django.shortcuts import render
from django.http import HttpResponse

import operator
import os
import loadme
import statsloaderx
from mccme.models import Problem, UserProfile

#from pre_test import *

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
    return HttpResponse('user_stats: ' + uid + '\nsuccess: ' + str(cuser.solved_problems.all()) + '\n' + str(cuser.unsolved_problems.all()))
    # return render(request, 'mccme/problems.html', {
    #     'problems_solved': cuser.solved_problems.all(), 'problems_unsolved': cuser.unsolved_problems.all()
    #     })

#def add_user(request):
# TO BE DONE LATER    
