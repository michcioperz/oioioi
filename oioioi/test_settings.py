# pylint: disable=wildcard-import
from oioioi.default_settings import *

TIME_ZONE = 'UTC'

SITE_ID = 1

ADMINS = (
    ('Test admin', 'admin@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

# Enable optional modules.
INSTALLED_APPS = (
    'oioioi.contestlogo',
    'oioioi.teachers',
    'oioioi.participants',
    'oioioi.testrun',
    'oioioi.scoresreveal',
    'oioioi.contestexcl',
    'oioioi.forum',
    'oioioi.disqualification',
    'oioioi.ctimes',
    'oioioi.acm',
    'oioioi.suspendjudge',
    'oioioi.submitservice',
    'oioioi.statistics',
    'oioioi.testspackages',
    'oioioi.notifications',
    'oioioi.mailsubmit',
    'oioioi.globalmessage',
    'oioioi.simpleui',
    'oioioi.usergroups',
    'oioioi.problemsharing',
    'oioioi.usercontests',
) + INSTALLED_APPS

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'oioioi.contestlogo.processors.logo_processor',
    'oioioi.contestlogo.processors.icon_processor',
    'oioioi.globalmessage.processors.global_message_processor',
]

AUTHENTICATION_BACKENDS += (
    'oioioi.base.tests.IgnorePasswordAuthBackend',
    'oioioi.teachers.auth.TeacherAuthBackend',
    'oioioi.usercontests.auth.UserContestAuthBackend',
)

MIDDLEWARE += (
    'oioioi.base.tests.FakeTimeMiddleware',
)

TESTS = True
MOCK_RANKINGSD = True

SECRET_KEY = 'no_secret'
COMPRESS_ENABLED = False
COMPRESS_PRECOMPILERS = ()
CELERY_ALWAYS_EAGER = True
SIOWORKERS_BACKEND = 'oioioi.sioworkers.backends.LocalBackend'
FILETRACKER_CLIENT_FACTORY = 'filetracker.client.dummy.DummyClient'
FILETRACKER_URL = None
USE_UNSAFE_EXEC = True
USE_LOCAL_COMPILERS = True
USE_UNSAFE_CHECKER = True

USE_SINOLPACK_MAKEFILES = True
SINOLPACK_RESTRICT_HTML = False


WARN_ABOUT_REPEATED_SUBMISSION = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

CONFIG_VERSION = INSTALLATION_CONFIG_VERSION

STATIC_ROOT = ''

# Do not print migrations DEBUG to console.
LOGGING['loggers']['django.db.backends.schema'] = {
    'handlers': ['console'],
    'level': 'INFO',
}
