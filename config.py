import os
import subprocess

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# http://clsc.net/tools-old/random-string-generator.php
SECRET_KEY = 'my precious'

# Connect to the Heroku Postgre database by grabbing the url out of the heroku config
# command.  That way we DEFINITELY know what the URL is.
# database_url = subprocess.check_output(['heroku', 'config:get', 'DATABASE_URL', '-a', 'groupbot-app'], shell=True)
# print "About to try and connect to ", database_url

# By using environ.get here, it checks for a 'DATABASE_URL' value and then automatically used the second
# thing if it doesn't find anything.
if os.environ.get('DATABASE_URL') is not None:
    print "Connecting to Heroku at " + os.environ.get('DATABASE_URL')

TEST_DATABASE_URI = 'sqlite:////Users/John/Dropbox/independent_work/groupbot/groupbot/test.db'

SQLALCHEMY_BINDS = {
    'default': os.environ.get('DATABASE_URL'),
    'dev': 'postgresql://postgres:Rawrqed123@localhost/groupbot_data',
    'testing':TEST_DATABASE_URI
}

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', SQLALCHEMY_BINDS['dev'])

# This tells SQLAlchemy-Migrate where to put its junk.
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
