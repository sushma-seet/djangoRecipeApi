'''
Testing commands

'''

from time import sleep
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError

from django.core.management import call_command
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    
    def test_wait_for_db(self,patch_checks):
        '''
        Testing wait for db function
        '''
        patch_checks.return_value = True
        
        call_command('wait_for_db')
        patch_checks.assert_called_once_with(databases = ['default'])
        
        
    @patch('time.sleep')
    def test_wait_for_db_delay(self,patch_sleep,patch_checks):
        '''
        Testing wait for db delay function
        '''
        
        patch_checks.side_effect = [Psycopg2Error] *2 + [OperationalError]*3+[True]
        call_command('wait_for_db')
        
        self.assertEqual(patch_checks.call_count ,6)
        patch_checks.assert_called_with(databases = ['default'])
        