from django.core.management.base import BaseCommand, CommandError

import operator
import os
import loadme
from mccme.models import Problem

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        print os.path.join(os.path.dirname(__file__))
        with open(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'plist.txt'), 'r') as plist:
            content = plist.readlines()
        print len(content)

        urlrangex = list()

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
        print len(stats)
        with open(os.path.join(os.path.join(os.path.dirname(__file__)), 'out.txt'), 'w') as sto:
            sto.write(str(stats))

        problems_in_db = Problem.objects.all()
        for pid, submits in stats.iteritems():
            problems= problems_in_db.filter(pid=pid)
            if problems:
                if problems[0].submits != submits:
                    problems[0].submits = submits
                    problems[0].save()
            else:
                problem = Problem()
                problem.pid = pid
                problem.submits = submits
                problem.save()
