import string

PUBLIC_ENDPOINTS = [
    'radar.index',
    'auth.login',
    'auth.forgot_username',
    'auth.forgot_password',
    'auth.reset_password',
    'static',
    'news.view_story_list',
    'news.view_story',
]

RESET_PASSWORD_MAX_AGE = 86400

GENERATE_PASSWORD_ALPHABET = string.ascii_letters + string.digits
GENERATE_PASSWORD_LENGTH = 10

PASSWORD_REGEXES = [
    '.{8,}',  # 8 characters
    '[a-z]',  # lowercase
    '[A-Z]',  # uppercase
    '[0-9]',  # number
]
PASSWORD_POLICY = 'Must be at least 8 characters and include: a lowercase letter, an uppercase letter and a digit.'
