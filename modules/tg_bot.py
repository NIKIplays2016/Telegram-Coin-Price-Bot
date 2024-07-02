import telebot
import datetime
import psycopg2
import json
from ..config import telegram_bot_token
from ..config import db_password


token= telegram_bot_token
bot=telebot.TeleBot(token)

connection = psycopg2.connect(
    dbname="userbase",
    user="postgres",
    password=db_password,#3-cr4td
    host="localhost"
)

def bot_write(id, sms):
    global bot
    try:
        bot.send_message(id,sms)
    except:
        print(f"bot was blocked by the {id}")


def get_sestings() -> dict:
    with open(R"base\settings.json") as file:
        settings = json.load(file)
    return settings

def save_settings(settings) -> None:
    with open(R"base\settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False)

def get_statick_info() -> dict:
    with open("base\static.json", "r") as file:
        token_base = json.load(file)
    return token_base

def save_statick_info(static) -> None:
    with open(R"base\statick.json", "w", encoding="utf-8") as file:
        json.dump(static, file, ensure_ascii=False)


####################################################

def update_user_data(user_base) -> None:
    user_id = user_base['id']
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        user_list = [
            str(user_base['spam']['coins']), user_base['spam']['delay'], user_base['spam']['time'],
            str(user_base['warning']['coins']),str(user_base['warning']['limits']),
            user_base['action'], user_base["ban"]
            ]
        cursor.execute("UPDATE users SET spam_coins = %s, delay = %s, time = %s, warning_coins = %s, limits = %s, actions = %s, ban = %s WHERE user_id=%s", (*user_list, user_id,))
        connection.commit()
        cursor.close()
    else:
        cursor.close()
        raise ValueError("Not found user")

def update_user_local_data(user_id, field_name, new_field) -> None: 
    """Important! Observe the data type"""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.execute(f"UPDATE users SET {field_name} = %s WHERE user_id = %s", (new_field, user_id))
        connection.commit()
        cursor.close()
    else:
        cursor.close()
        raise ValueError("Not found user")


def get_user_dict(user_id) -> dict:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user_data = cursor.fetchone()

    base = {}

    if user_data:
        base['id'] = user_data[0]
        base['name'] = user_data[1]
        base['root'] = user_data[2]

        base['spam'] = {}
        try:
            base['spam']['coins'] = eval(user_data[3])
        except:
            base['spam']['coins'] = []
        base['spam']['delay'] = user_data[4]
        base['spam']['time'] = user_data[5]

        base['warning'] = {}
        try:
            base['warning']['coins'] = eval(user_data[6])
        except:
            base['warning']['coins'] = []

        try:
            base['warning']['limits'] = eval(user_data[7])
        except:
            base['warning']['limits'] = []
        
        base['action'] = user_data[8]
        base['ban'] = user_data[9]
    else:
        print(f"Пользователь с id {user_id} не найден")

    cursor.close()
    return base


def check_registrate(user_id) -> bool:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user_data = cursor.fetchone()
    
    cursor.close()
    
    if user_data:
        return True
    else:
        return False


def check_ban(user_id) -> bool:
    cursor = connection.cursor()
    ban = cursor.execute("SELECT ban FROM users WHERE user_id=%s", (user_id,))
    cursor.close()
    return ban


def check_valid(message) -> bool:
    if not check_registrate(message.chat.id):
        bot.reply_to(message, "Для использования комманд нужно зарегестрироваться. \nВведите пароль.")
        return False
    elif check_ban(message.chat.id):
        bot.reply_to(message, f"Вы были заблокированы.😬 \nПоддержка: @picard_off")
        return False
    else:
        return True
    
def check_admin(message):
    try:
        base = get_user_dict(message.from_user.id)
        if base["root"]:
            return True
        else:
            bot.reply_to(message, "У вас нет прав для этой команды")            
            return False
    except:
        bot.reply_to(message, "У вас нет прав для этой команды")
        return False
        

#############################################

def registrate(message) -> None:
    cursor = connection.cursor()
    id = message.chat.id
    if id > 0:
        name = message.from_user.username
    elif id < 0:
        name = message.chat.title

    cursor.execute("INSERT INTO users(user_id, name, root, spam_coins, delay, time, warning_coins, limits, actions, ban, date_of_registration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, name, False, "", 1, datetime.datetime.now(), "", "", 0, False, datetime.datetime.now()))
    connection.commit()
    cursor.close()

    bot.reply_to(message, text="Successful registration")


def bot_main() -> None:
    global bot
    settings = get_sestings()
    token_base = get_statick_info()

    """def check_admin(message, base) -> bool:

        try:
            chat_index = base["id"].index(message.chat.id)
        except:
            return False

        try:
            user_index = base["id"].index(message.from_user.id)
        except:
            return False

        if base["root"][chat_index] or base["root"][user_index]:
            return True
        else:
            return False"""


    #def reset_actions():
    #    return [False, False, False, False, False, False, False, False]


    @bot.message_handler(commands=['start'])
    def handle_start(message):
        id = message.chat.id
        
        if check_registrate(id):
            bot.reply_to(message, "Воспользуйтесь командой /help")
        else:
            bot.reply_to(message, "Введите пароль")
       



    @bot.message_handler(commands=['command1'])
    def handle_start(message):
        if not check_valid(message):
            return 0
        
        id = message.chat.id
        base = get_user_dict(id)

        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
        for i in token_base["tokens"]:
            keyboard1.row(i)

        bot.reply_to(message, "Введите короткое название монеты", reply_markup=keyboard1)
        update_user_local_data(id, "actions", 7)


    @bot.message_handler(commands=['command2'])
    def handle_start(message):
        if not check_valid(message):
            return 0
        
        id = message.chat.id
        base = get_user_dict(id)
        bot.reply_to(message, "Введите через пробел короткое называние монеты и пределы. \n\nПример: \TON 6.43 7.1")

        update_user_local_data(id, "actions", 1)


    @bot.message_handler(commands=['command3'])  # Удаление монеты из warning
    def handle_start(message):
        if not check_valid(message):
            return 0
       
        id = message.chat.id
        base = get_user_dict(id)

        update_user_local_data(id, "actions", 6)
        bot.reply_to(message, "Введите короткое название монеты")


    @bot.message_handler(commands=['cooldown'])
    def handle_start(message):
        if not check_valid(message):
            return 0
       
        id = message.chat.id
        base = get_user_dict(id)

        update_user_local_data(id, "actions", 8)
        bot.reply_to(message, f"Введите интервал в минутах между уведомленими \nот 1 до 2880")


    @bot.message_handler(commands=['about_me'])
    def handle_start(message):
        if not check_valid(message):
            return 0
       
        id = message.chat.id
        base = get_user_dict(id)

        sms = f"id: {id}"

        sms += "\n\nУведомления о цене:"
        sms += f"\n{base['spam']['coins']}"
        sms += f"\n Переодичность: {base['spam']['delay']}м"

        sms += "\n\nУведомления при выходе монеты из ценового диапазона:\n"
        for i in range(len(base['warning']['coins'])):
            sms += f"\nМонета: {base['warning']['coins'][i]} \nЦеновой диапазон: с {base['warning']['limits'][i][0]} до {base['warning']['limits'][i][1]}\n"

        bot.reply_to(message, sms)


    @bot.message_handler(commands=['command0', "help", "info"])
    def handle_start(message):
        bot.reply_to(
            message,
            text=f""" 
'Coin price' - Это Telegram бот позволяющий следить за ценой разных криптовалют.
v1.0 Beta

Информация о цене берется с okx.com

Команды:
 /command1 - При вводе этой команды бот будет присылать каждую минуту цену (по умолчанию, чтобы изменить: /cooldown) на введенную вами монету, чтобы отписаться нужно повторно ввести команду.

 /command2 - При вводе этой команды бот предлагает вам ввести название монеты, верхний и нижний "предел" цены. 
При переходе нижнего или верхнего предела цены, бот уведомит вас об этом. 

 /command3 - При вводе этой комманды нужно ввести название монеты, и вам больше не будут приходить уведомления о выходе цены этой манеты из ценового диапазона который вы указали ранее (/command2)  

 /cooldown - Эта команда позволяет изменить с какой частотой в минутах, бот будет присылать вам цену (от 1 минуты до 2880(2 дня))

 /about_me - Бот выведет информацию о вас
 
@picard_off
19.05.2024
okx API 
               """
        )

    @bot.message_handler(commands=['id_list'])
    def handle_start(message):
        if not check_admin(message):
            return 0

        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name FROM users")
        """
        rows = cursor.fetchall()
        cursor.close()
        
        indexes = rows[0]
        names = rows[1]

        sms = ""
        for i in range(len(indexes)):
            sms += f"\n {i}: {names[i]} - {indexes[i]}"
        """
        users = cursor.fetchall()

        sms = ""
        for i in range(len(users)):
            sms += f"\n {i}: {users[i][1]} - {users[i][0]}"
        cursor.close()

        bot.reply_to(message, sms)

    @bot.message_handler(commands=['admin'])
    def handle_start(message):
        if not check_admin(message):
            return 0

        bot.reply_to(message, "Команды Администратора: \n/id_list \n/ban \n/black_list \n\nКоманды главного Администратора: \n/add_admin \n/delete_admin \n/change_main_admin ")


    @bot.message_handler(commands=["add_admin"])
    def handle_start(message):
        id = message.from_user.id

        sestings=get_sestings()

        if not id == sestings["main_admin"]:
            bot.reply_to(message, "У вас нет прав для этой команды. Это может делать только главный админ")
            return 0

        update_user_local_data(id, "actions", 3)
        bot.reply_to(message, "Введите id пользователя")


    @bot.message_handler(commands=["delete_admin"])
    def handle_start(message):
        id = message.from_user.id

        sestings=get_sestings()

        if not id == sestings["main_admin"]:
            bot.reply_to(message, "У вас нет прав для этой команды. Это может делать только главный админ")
            return 0

        update_user_local_data(id, "actions", 4)
        bot.reply_to(message, "Введите id пользователя")


    @bot.message_handler(commands=["change_main_admin"])
    def handle_start(message):
        id = message.from_user.id

        sestings=get_sestings()

        if not id == sestings["main_admin"]:
            bot.reply_to(message, "У вас нет прав для этой команды. Это может делать только главный админ")
            return 0

        update_user_local_data(id, "actions", 5)
        bot.reply_to(message, "Введите id пользователя")


    @bot.message_handler(commands=['ban'])
    def handle_start(message):
        id = message.from_user.id
        if not check_admin(message):
            return 0

        update_user_local_data(id, "actions", 2)
        bot.reply_to(message, "Введите id и действие(0 - убрать из чс, 1 - добавить в чс) \n\nПример: \n1913991 1")




    @bot.message_handler(commands=['black_list'])
    def handle_start(message):
        id = message.from_user.id
        base = get_user_dict(id)

        if not check_admin(message):
            return 0

        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name FROM users WHERE ban=%s", (True,))
        users = cursor.fetchall()
        cursor.close()

        if len(users) == 0:
            bot.reply_to(message, "Черный список пуст")
        else:
            sms = ""
            for i in range(len(users)):
                try:
                    sms += f"\n {i}: {users[i][1]} - {users[i][0]}"
                except:
                    sms += f"\n {i}: Noname - {users[i][0]}"
            bot.reply_to(message, sms)






#######################################################################################################################
    @bot.message_handler(content_types=['text', 'document', 'audio', 'photo', 'video'])
    def get_text_messages(message):
        id = message.chat.id
        pid = message.from_user.id
        
        if not check_registrate(id):
            if message.text == settings['password']:
                registrate(message)
            else:
                bot.reply_to(message, text="Не верный пароль")
                bot.send_message(id, "Введите пароль заново")
            return 0

        base = get_user_dict(id)
        user_base = get_user_dict(pid)
        if base["ban"] and id > 0 and not user_base['root']:
            bot.reply_to(message, f"Вы были заблокированы.😬 \nПоддержка: @picard_off")
            return 0
        elif base["ban"] and id < 0 and not user_base['root']:
            return 0


        if base['action'] == 1:
            try:
                command = message.text.split(" ")
                token, command[1], command[2] = command[0].upper(), float(command[1]), float(command[2])
            except:
                bot.reply_to(message, "❌Неверный ввод❌ \nПопробуйте заново нажав на команду /command2")
                update_user_local_data(id, "actions", 0)
                return 0

            if not token in token_base["tokens"]:
                bot.reply_to(message, "Такой монеты нет в списке")
                update_user_local_data(id, "actions", 0)
                return 0


            if token in base["warning"]["coins"]:
                token_index = base["warning"]["coins"].index(token)
                base["warning"]["limits"][token_index] = [command[1], command[2]]
            else:
                base["warning"]["coins"].append(token)
                base["warning"]["limits"].append([command[1], command[2]])
            
            bot.reply_to(message, f"Теперь вам будет приходить уведомление когда цена {token} \nПовысится до {command[2]}$ \nУпадет до {command[1]}$")
            update_user_data(base)
            update_user_local_data(id, "actions", 0)


        elif user_base['action'] == 2:
            command = message.text.split(" ")
            try:
                command[0], command[1] = int(command[0]), int(command[1])
            except:
                bot.reply_to(message, "Ошибка ввода")
                update_user_local_data(pid, "actions", 0)
                return 0

            try:
                if command[1] == 0:
                    update_user_local_data(command[0], "ban", False)
                    bot.reply_to(message, f"Пользователь {command[0]} теперь не в черном списке")
                elif command[1] == 1:
                    update_user_local_data(command[0], "ban", True)
                    bot.reply_to(message, f"Пользователь {command[0]} теперь в черном списке")
            except:
                bot.reply_to(message, "Такого пользователя нет")

            update_user_local_data(pid, "actions", 0)

        elif  user_base['action'] == 3:
            try:
                nid = int(message.text)
            except:
                bot.reply_to(message, "Неверный ввод")
                update_user_local_data(pid, "actions", 0)
                return 0

            try:
                update_user_local_data(nid, "root", True)
                bot.reply_to(message, f"Пользователь {nid} теперь администратор")
            except:
                bot.reply_to(message, f"Пользователь {nid} не найден")
            update_user_local_data(pid, "actions", 0)
            


        elif  user_base['action'] == 4:
            try:
                nid = int(message.text)
            except:
                bot.reply_to(message, "Неверный ввод")
                update_user_local_data(pid, "actions", 0)
                return 0

            try:
                update_user_local_data(pid, "actions", 0)
                update_user_local_data(nid, "root", False)
                bot.reply_to(message, f"Пользователь {nid} теперь не администратор")

            except:
                bot.reply_to(message, f"Пользователь {nid} не найден")

            update_user_local_data(pid, "actions", 0)


        elif  user_base['action'] == 5:
            try:
                nid = int(message.text)
            except:
                bot.reply_to(message, "Неверный ввод")
                update_user_local_data(pid, "actions", 0)
                return 0

            bot.reply_to(message, f"Главный админ изменен с {base['main_admin']} на {nid}")
            settings["main_admin"] = nid
            save_settings(settings)
            update_user_local_data(pid, "actions", 0)


        elif  base['action'] == 6: #Удаление токена с warning
            token = message.text.upper()

            if token in base["warning"]["coins"]:
                token_index = base["warning"]["coins"].index(token)
                base["warning"]["coins"].remove(token)
                base["warning"]["limits"].pop(token_index)
                bot.reply_to(message, f"Теперь вам не будет приходить уведомление о {token}")
            else:
                bot.reply_to(message, f"У вас не стоит 'колокольчик' на {token}")
            update_user_data(base)
            update_user_local_data(id, "actions", 0)
            

        elif  base['action'] == 7:
            sms = message.text.upper()
            if not sms in token_base["tokens"]:
                bot.reply_to(message, "Такой монеты к нет в списке")
                update_user_local_data(id, "actions", 0)
                return 0

            if sms in base["spam"]["coins"]:
                base["spam"]["coins"].remove(sms)
                bot.reply_to(message, f"Теперь вы не будете получать рассылку цены на {sms}")
            else:
                base["spam"]["coins"].append(sms)
                bot.reply_to(message, f"Теперь вы будете получать рассылку цены на {sms}")
            update_user_data(base)
            update_user_local_data(id, "actions", 0)

        elif  base['action'] == 8:
            sms = message.text
            try:
                minutes = int(sms)
            except:
                bot.reply_to(message, f"Не верный ввод: {sms} \nПопробуйте заново")
                update_user_local_data(id, "actions", 0)
                return 0

            if not (minutes >= 1 and minutes <= 2880):
                bot.reply_to(message, f"{minutes} минут не входит в интервал 1-2880\nПопробуйте заново")
                update_user_local_data(id, "actions", 0)
                return 0

            base['spam']['delay'] = minutes
            base['spam']['time'] = datetime.datetime.now()
            base['action'] = 0
            update_user_data(base)
            bot.reply_to(message, f"Теперь уведомление о цене будет приходить вам каждые {minutes}м")
            



    bot.polling(none_stop=True, interval=0)