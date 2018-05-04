from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in settings.ADMINS:
            username = user[0].replace(' ', '')
            email = user[1]
            password = user[2]

            if not User.objects.filter(username=username).exists():
                print('Creating account for %s (%s)' % (username, email))
                User.objects.create_superuser(username, email, password)
            else:
                print('Admin accounts can only be'
                      'initialized if no Accounts exist')
