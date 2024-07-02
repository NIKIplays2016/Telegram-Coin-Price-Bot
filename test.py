import datetime
from modules.tg_bot import *

user_base = get_user_dict(852663786)

print(user_base['spam']['delay'])


time_difference = datetime.datetime.now() - user_base['spam']['time']
minutes_difference = time_difference.total_seconds() // 60

print(minutes_difference)