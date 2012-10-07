import ConfigParser
from django.conf import settings

def setup(conffile):
    conf = ConfigParser.SafeConfigParser()
    conf.read([conffile])
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': conf.get('database', 'dbname'),
                'USER': conf.get('database', 'dbuser'),
                'PASSWORD': conf.get('database', 'dbpass'),
                'HOST': conf.get('database', 'dbhost'),
                },
            'forum': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': conf.get('forumdb', 'dbname'),
                'USER': conf.get('forumdb', 'dbuser'),
                'PASSWORD': conf.get('forumdb', 'dbpass'),
                'HOST': conf.get('forumdb', 'dbhost'),
                },
            }
        )
