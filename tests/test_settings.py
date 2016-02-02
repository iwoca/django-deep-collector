import django


SECRET_KEY = 'WE DONT CARE ABOUT IT'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'keepdb.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS = ('tests', )


# Using DiscoverRunner before Django 1.6 to be able to use test files with 'test*' pattern name
if django.VERSION < (1, 6):
    INSTALLED_APPS += ('discover_runner', )
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
