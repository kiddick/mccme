from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        with open(os.path.join('/home/django/django_project/mccme','plist.txt'), 'r') as plist:
            content = plist.readlines()
        print len(content)