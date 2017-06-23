from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import unicodedata
import traceback
import sys
import threading
import time

class Currency:
    def __init__(self):
        self.name = None
        self.value = None
        self.dateCreated = None
        self.firstPrice = None
        self.script = None
    def hasAddInfo(self):
        if self.brithDay == None:
            return False
        return True

def getAddInfo(url, instance):
    add_text = requests.get(url).text
    print ('got data '+url+'\n')
    add_text = BeautifulSoup(add_text,"lxml")
    rawScriptTuple = add_text.find('td', {'colspan':'2'}).find_all('script')
    print ('parsing data \n')
    for item in rawScriptTuple:
        rawScript = item.text
        if rawScript != '':
            break
    ret = rawScript[rawScript.rindex('else { var dydata'):]
    instance.script = ret

result = []
raw = requests.get('https://bitinfocharts.com/ru/markets/')
text = raw.text
soup = BeautifulSoup(text, 'lxml')

currencies = soup.find('div', {'align':'left', 'class':'ma-w1','style':'margin:auto;'}).find_all('tr', {'class':'ptr'})

for currency in currencies:
    instance = Currency()
    add_text = ''
    dateCreated = ''
    rawScript = ''
    scriptContent = ''
    valueEarliest = ''
    currencyCells = currency.find_all('td')
    instance.name = currencyCells[0].get('data-val')
    instance.value = currencyCells[1].get('data-val')
    try:
        urlTail = currencyCells[0].find('a').get('href')
        url = 'https://bitinfocharts.com/ru/'+urlTail[3:]
        scriptContent = None
        addThread = threading.Thread(target = getAddInfo, args =(url,instance))
        addThread.start()
        for i in range (0,10):
            time.sleep(0.5)
            print ('sleep...\n')
            if instance.script != None:
                break
        if instance.script == None:
            raise Exception 
        instance.dateCreated = re.search('new Date\((.*?)\)', instance.script).group(1)
        instance.firstPrice = re.search('new Date.*?\[.*?,(.*?),', instance.script).group(1)
        instance.script = None
    except:
        print(''.join(traceback.format_exception(*sys.exc_info())))
        instance.dateCreated = None
        instance.firstPrice = None  
    result.append(instance)
    print('\n\ndone with '+instance.name+'\n\n')

for item in result:
    if item.hasAddInfo():
        print("currency:{}, value:{}, date:{}, firstSoldAt:{}".format(item.name,item.value,item.firstPrice,item.valueEarliest))

