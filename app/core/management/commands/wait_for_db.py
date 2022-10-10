'''
commands to wait app until db is ready
'''
import time
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''
    commands to wait
    '''
    
    def handle(self, *args, **option):
        self.stdout.write('waiting for database')
        db_up =False
        while db_up is False:
            try:
                self.check(databases = ['default'])
                db_up =True
            except(Psycopg2Error, OperationalError):
                self.stdout.write('database not ready yet...wait for sencond')
                time.sleep(1)
                
        self.stdout.write(self.style.SUCCESS('database available'))