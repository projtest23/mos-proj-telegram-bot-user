from telegram import *
import telegram.ext
from datetime import datetime
import requests
import cache
from decouple import config


TOKEN = config("TOKEN", default="")
ADMIN_CHAT_ID = config("ADMIN_CHAT_ID", default="")
Programmer_CHAT_ID = config("PROGRAMMER_CHAT_ID", default="")
address = config("ADDRESS", default="")

msg_id = cache.msg_id
reg_log_data= cache.reg_log_data
command_status = cache.command_status
command_data = cache.command_data


def check_registration(user_id):
    try:
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id']) == str(user_id):
                return ('you already registered.')
    except:
        return ('something happend, we could not connect to server')
    return ('input your username')

def check_not_command(text):
    if(text != "register" and 
        text != "close all positions" and 
        text != "emergency shotdown" and 
        text != "veiw staking reward date" and 
        text != "withdraw" and 
        text != "stop staking" and 
        text != "start staking" and 
        text != "deposit" and 
        text != "total balance" and 
        text != "login"):
        return True
    else:
        return False


def register_status(user_id,msg):
    if 'username' not in reg_log_data[user_id].keys(): 
        reg_log_data[user_id].update({'username':msg})
        return {"k":False,"text":"input your one_inch wallet address"}

    elif 'one_inch' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'one_inch':msg})
        return {"k":False,"text":"input your uniswap wallet address"}

    elif 'uniswap' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'uniswap':msg})
        return {"k":False,"text":"input your atomic wallet address"}

    elif 'atomic' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'atomic':msg})
        return {"k":False,"text":"input your password"} 

    elif 'password' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'password':msg})
        keyboard = [[InlineKeyboardButton("yess",callback_data='register'),
                    InlineKeyboardButton("noo",callback_data='again')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"""
                your username: '{reg_log_data[user_id]['username']}'
your password: '{reg_log_data[user_id]['password']}' 
your atomic: '{reg_log_data[user_id]['atomic']}'
your uniswap: '{reg_log_data[user_id]['uniswap']}'
your one_inch: '{reg_log_data[user_id]['one_inch']}'"""
        command_status[user_id] = ''
        return {"k":True,"text":text, "reply_markup":reply_markup}
    

def login_status(user_id,msg):
    if 'username' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'username':msg})
        return {"text":"input your password",'login':False}

    elif 'password' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'password':msg})
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not (user['username'] == reg_log_data[user_id]['username'] and user['password'] == reg_log_data[user_id]['password']):
                    reg_log_data['command_status'] = ""
                    return {"text":"please check your inputs, username or password is wrong",'login':False}
                req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
                data = req.json()
                for user in data:
                    if str(user['telegram_user']) == str(user_id):
                        buttons = [[KeyboardButton("total balance")],
                    [KeyboardButton("deposit")],
                    [KeyboardButton("start staking")],
                    [KeyboardButton("stop staking")],
                    [KeyboardButton("withdraw")],
                    [KeyboardButton("emergency shotdown")],
                    [KeyboardButton("veiw staking reward date")],
                    [KeyboardButton("close all positions")]]
                        reply_markup=ReplyKeyboardMarkup(buttons)
                        
                        command_status[user_id] = ''
                        return {"login":True,"text":"welcome!", "reply_markup":reply_markup}
                return {"text":"your account is not confirmed, please be patient",'login':False}
        return {"text":"you are not a user, please register first",'login':False}


def choosing_wallet(user_id,msg_text):
    req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
    data = req.json()
    keyboard = []
    flag = False
    for user in data:
        if str(user['telegram_user']) == str(user_id):
            if msg_text == 'deposit':
                command_status[user_id] = "deposit"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"deposit:{user['name']}")])

            elif msg_text == 'total balance':
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"balance:{user['balance']},{user['name']}")])
            
            elif msg_text == 'veiw staking reward date':
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"wallet_id:{user['id']},{user['name']}")])
            
            elif msg_text == 'start staking':
                command_status[user_id] = "start_staking"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"start_staking:{user['id']},{user['name']}")])
            
            elif msg_text == 'stop staking':
                command_status[user_id] = "stop_staking"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"stop_staking:{user['id']},{user['name']}")])
            
            elif msg_text == 'withdraw':
                command_status[user_id] = "withdraw"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"withdraw:{user['id']},{user['name']}")])
            
            elif msg_text == 'close all positions':
                command_status[user_id] = "close_positions"
                command_data[user_id] = {'wallet':user['name'],"wallet_id":user['id']}
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"close_positions:{user['id']},{user['name']}")])
            
            elif msg_text == 'emergency shotdown':
                command_status[user_id] = "emergency"
                command_data[user_id] = {'wallet':user['name'],"wallet_id":user['id']}
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"emergency:{user['id']},{user['name']}")])

            flag = True

    if flag:
        reply_markup = InlineKeyboardMarkup([keyboard])
        text = f"""please choose the wallet"""
        return {"k":True,"text":text, "reply_markup":reply_markup}
    else:
        return {"k":False,"text":'you have no active wallet'}
    

def start_staking(user_id, msg,message_id):
    global command_data
    global msg_id
        
    if 'volume' not in command_data[user_id].keys():
        volume = msg
        if not volume.isdigit():
            msg_id=0
            return {"text":"your volume is not an integer number, please click on start staking an start again","stake":False}
        command_data[user_id].update({'volume':volume})
        msg_id = message_id
        return {"text":"input staking date(your number unit will be month","stake":False}
    if 'date' not in command_data[user_id].keys():
        date = msg
        if not date.isdigit():
            msg_id=0
            command_data = {}
            return {"text":"your volume is not an integer number, please click on start staking and start again","stake":False}
            
        command_data[user_id].update({'date':date})
        msg_id = message_id
        return {"text":"input your password","stake":False}
    else:
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not str(user['password']) == str(msg):
                    reg_log_data['command_status'] = ""
                    return {"text":"please check your inputs, password is wrong","stake":False}
                    
        req_data = {
            "wallet": command_data[user_id]['wallet_id'],
            "telegram_user": user_id,
            "staking_volume": int(command_data[user_id]['volume']),
            "staking_date": int(command_data[user_id]['date']),
            "created_date":datetime.now().date()
        }
        req = requests.post(f"http://{address}/dydx/api/v1/staking/",req_data)
        if req.status_code == 201:
            return {"text": "your staking is complited","stake":True}
        elif req.status_code == 400:
            return {"text":req.json(),"stake":False}


def close_positions(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"please check your inputs, password is wrong","k":False}
            break
    
    keyboard = [[InlineKeyboardButton("yess",callback_data='close_yes'),
                    InlineKeyboardButton("noo",callback_data='close_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "are you sure that you want to close all positions, it might harm your account financially!"
    return {"k":True,"text":text, "reply_markup":reply_markup}


def emergency_shotdown(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"please check your inputs, password is wrong","k":False}
            break
    
    keyboard = [[InlineKeyboardButton("yess",callback_data='shotdown_yes'),
                    InlineKeyboardButton("noo",callback_data='shotdown_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "are you sure that you want to shot down your wallet, it might harm your account financially!"
    return {"k":True,"text":text, "reply_markup":reply_markup}


def stop_staking(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"please check your inputs, password is wrong","k":False}
            break
    req = requests.get(f"http://{address}/dydx/api/v1/staking/")
    data = req.json()
    keyboard = []
    stakes_list = []
    for stake in data:
        if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
            stakes_list.append(stake)
    
    text = """please choose one of your staking!"""              
    if len(stakes_list)== 0:
        text = "you have no stake"
    else:
        for s in range(len(stakes_list)):
            keyboard.extend([InlineKeyboardButton(f"{s+1}",callback_data=f"choose_stake:{stakes_list[s]['staking_volume']},{stakes_list[s]['staking_date']}")])
            text += f"""
{s+1}. volume: {stakes_list[s]['staking_volume']} , date: {stakes_list[s]['staking_date']}"""
    reply_markup = InlineKeyboardMarkup([keyboard])
    
    return {"k":True,"text":text, "reply_markup":reply_markup}



def withdraw(user_id, msg,message_id):
    global command_data
    global msg_id
        
    if 'password' not in command_data[user_id].keys():
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not str(user['password']) == str(msg):
                    reg_log_data['command_status'] = ""
                    return {"text":"please check your inputs, password is wrong","withdraw":False}
        command_data[user_id].update({'password':msg})
        msg_id = message_id
        return {"text":"input the volume of withdraw","withdraw":False}
    
    if 'volume' not in command_data[user_id].keys():
        volume = msg
        if not volume.isdigit():
            msg_id=0
            return {"text":"your volume is not an integer number, please click on withdraw and start again","withdraw":False}
         
        command_data[user_id].update({'volume':volume})
        msg_id = message_id
        req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
        wallets = req.json()
        req_stake = requests.get(f"http://{address}/dydx/api/v1/staking/")
        stakes = req_stake.json()
        req_stake = requests.get(f"http://{address}/dydx/api/v1/staking/")
        stakes = req_stake.json()
        req_position = requests.get(f"http://{address}/dydx/api/v1/allpositions/")
        positions = req_position.json()
        balance = 0
        
        for wallet in wallets:
            if str(wallet['id']) == str(command_data[user_id]['wallet_id']):
                balance = wallet['balance']
        all_stake = 0
        for stake in stakes:
            if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
                all_stake += stake['staking_volume']
        free_margin = balance - all_stake
        if (free_margin)<float(volume):
            return {"text":f"your margin is less than this volume, free margin:{round(free_margin,2)}","withdraw":False}
        for stake in stakes:
            if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
                all_stake += stake['staking_volume']
        for pos in positions:
            if str(pos['wallet']) == str(command_data[user_id]['wallet_id']):
                return {"text":f"you can not withdraw because you have open positions","withdraw":False}
        new_balance = balance - float(volume)
        post_body = {
            "balance": new_balance
        }
        req = requests.patch(f"http://{address}/dydx/api/v1/wallet/{command_data[user_id]['wallet_id']}/",post_body)
        if req.status_code == 200:
            return {"text":"withdraw is under process please be patient","withdraw":True}
        else:
            return {"text":"sorry, server is down please try later","withdraw":False}