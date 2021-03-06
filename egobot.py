#!/usr/bin/python
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from json import loads
import requests
import _thread
import re 
from time import sleep

def alarmthread(update,context,stop,buses):
    slist = {15,12,10,5} # kaç dk kalınca söyleyeceği
    said = 0 # en son söylediği sayı
    while 1:
        timeleft = gettimeleft(stop,buses)
        for bus in timeleft:
            tf = timeleft[bus]
            if tf in slist and said != tf:
                    update.message.reply_text(f'{bus} kodlu otobüsün {stop} nolu durağa gelmesine {tf} dakika.')
                    said = tf
            elif tf == "Geldi":
                update.message.reply_text(f'{bus} kodlu otobüsün {stop} nolu durağa geldi.')
                return

            
            
    
def help(update: Update, context: CallbackContext) -> None:
        update.message.reply_text("Alarmı başlatmak için /alarm <Durak no> <hat kod(lar)> yazınız")

def startalarm(update: Update, context: CallbackContext) -> None:
    try:
        stop = context.args[0]
        buses = context.args[1:]
        _thread.start_new_thread(alarmthread, (update,context,stop,buses))
        update.message.reply_text(f'{stop} nolu durakta {buses} kodlu otobüsler için alarm başladı.')
    except:
         help(update,context)
    return

def initbot():
    with open('.token') as tokenf:
        updater = Updater(tokenf.read().splitlines()[0])
    
    updater.dispatcher.add_handler(CommandHandler('alarm', startalarm))
    updater.dispatcher.add_handler(CommandHandler('start', help))
    
    updater.start_polling()
    print("Bot Hazır!")
    updater.idle()
    
def gettimeleft(stop,buses):
    headers = {
        'User-Agent': 'EGO Genel Mudurlugu-EGO Cepte-ANDROID-Redmi-Redmi 9-osV:12-apV:4.0.4-lang:',
    }
    info = requests.get(f'https://egocptsrvand.ego.gov.tr/hibrit/srv.asp?&LAN=tr&FNC=Otobusler&DURAK={stop}', headers=headers)
    info = loads(info.content)["table"]
    times = {}
    for bus in info:
        hatkod = bus["hat_kod"]
        sure = bus["sure"]
        if hatkod in buses and not "sa" in sure and not "Sonraki Hareket Saati İlk Duraktan" in sure:
            try:
                sure = int(re.findall("\\d+",sure)[0])
            except:
                print("otobüsün süresi yok")
            if hatkod in times:
                if times[hatkod] > sure:
                    times[hatkod] = sure
            else:
                times[hatkod] = sure
    return times
