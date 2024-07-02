import datetime
from config import db_password
from modules.tg_bot import bot_main, bot_write, get_user_dict, check_ban
from modules.spot_price import *

import json

from threading import Thread
from time import sleep
import psycopg2

connection = psycopg2.connect(
    dbname="userbase",
    user="postgres",
    password= db_password,#3-cr4td
    host="localhost"
)


def update_user_time(user_id) -> None:
    cursor= connection.cursor()
    
    cursor.execute(f"UPDATE users SET time = %s WHERE user_id = %s", (datetime.datetime.now(), user_id))
    
    connection.commit()
    cursor.close()


def check_price():
    while True:

        with open("base\static.json", "r") as file:
            token_base = json.load(file)

        while True:
            price = get_price(token_base)
            keys_list = list(price.keys())

            if len(keys_list) == len(token_base["tokens"]):
                break
            print("#" * 1000)

        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        cursor.close()
        print(users)
        # spam
        for id in users:
            id = id[0]
            if check_ban(id):
                continue
            user_base = get_user_dict(id)

            time_difference = datetime.datetime.now() - user_base['spam']['time']
            minutes_difference = time_difference.total_seconds() // 60

            if minutes_difference > user_base['spam']['delay']:
                if user_base['spam']['delay'] > 1:
                    update_user_time(id)
                print(f"user {id} spam go")
                sms = ""
                for i in range(len(user_base['spam']['coins'])):
                    sms += f"\nЦена {user_base['spam']['coins'][i]}: {price[user_base['spam']['coins'][i]]}$"
                if not sms == "":
                    print(f"Bot write for user: {id}")
                    bot_write(id, sms)
            else:
                print(f"No cooldown {id}")

        # warning
        for id in users:
            id = id[0]
            if check_ban(id):
                continue
            user_base = get_user_dict(id)

            for b in range(len(user_base["warning"]["coins"])):
                local_token = user_base["warning"]["coins"][b]

                local_price = float(price[local_token])
                if local_price > user_base["warning"]["limits"][b][1]:
                    bot_write(
                        id,
                        f"❕💸💸💸 \nЦена {local_token}:{local_price} \n\n Достигнут лимит:{user_base['warning']['limits'][b][1]}"
                    )
                elif local_price < user_base["warning"]["limits"][b][0]:
                    bot_write(
                        id,
                        f"❗️🛑🛑🛑 \nЦена {local_token}:{local_price} \n\n Достигнут лимит:{user_base['warning']['limits'][b][0]}"
                    )

        '''

        for a in range(len(base["warning"]["token"])):
            user_id = base["id"][a]
            if not user_id in base["black_list"]:
                for b in range(len(base["warning"]["token"][a])):
                    local_token = base["warning"]["token"][a][b]

                    local_price = float(price[local_token])
                    if local_price > base["warning"]["limit"][a][b][1]:
                        bot_write(
                            user_id,
                            f"❕💸💸💸 \nЦена {local_token}:{local_price} \n\n Достигнут лимит:{base['warning']['limit'][a][b][1]}"
                        )
                    elif local_price < base["warning"]["limit"][a][b][0]:
                        bot_write(
                            user_id,
                            f"❗️🛑🛑🛑 \nЦена {local_token}:{local_price} \n\n Достигнут лимит:{base['warning']['limit'][a][b][0]}"
                        )



        for a in range(len(base["spam"]["token"])):
            user_id = base["id"][a]
            cooldown = base["spam"]["time"][a]
            if not user_id in base["black_list"] and (tick % cooldown == 0):
                print(f"user {user_id} spam go")
                sms = ""

                for i in range(len(base["spam"]["token"][a])):
                    sms += f"\nЦена {base['spam']['token'][a][i]}: {price[base['spam']['token'][a][i]]}$"
                if not sms == "":
                    bot_write(user_id, sms)

            else:
                print(f"No cooldown {a}")
        '''

        print(f"check_price() finish: {datetime.datetime.now()}")

        """
        for a in token_base["tokens"]:

            for i in range(len(base["id"])):

                limit = base["limit"][i]

                if base["Question"]["warning"][i] and not id in base["black_list"] and a in base["token"][i]:
                    if price < limit[0]:
                        bot_write(base["id"][i], f"❗️🛑🛑🛑 \nЦена NOT:{price} \n\n Достигнут лимит:{limit[0]}")
                    elif price > limit[1]:
                        bot_write(base["id"][i], f"❕💸💸💸 \nЦена Not:{price} \n\n Достигнут лимит:{limit[1]}")

                if base["Question"]["spam"][i] and not id in base["black_list"] and a in base["token"][i]:
                    bot_write(base["id"][i], f"Not: {price}")

            print("OK")
        """
        sleep(60)


if __name__ == "__main__":
    Thread(target=check_price).start()
    Thread(target=bot_main).start()