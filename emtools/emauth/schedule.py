import datetime

from emtools.emauth.userauth import authenticate_users

SCHEDULE = [("api-auth", authenticate_users, 60*12)]
