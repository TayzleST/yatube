from yatube.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# disable captcha during testing(you must manually set True)
CAPTCHA_TEST_MODE = True