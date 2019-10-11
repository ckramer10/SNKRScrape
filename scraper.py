import mechanize
from twilio.rest import Client
from bs4 import BeautifulSoup as bs
import time
import sys
import config

store_url = 'https://nike.com/launch'
client = Client(config.account_sid, config.auth_token)

#Shoes
snkrsPass = "SNKRS Pass"
caseNum = 'number'
lastShoeScan = set()
newShoeScan = set()
lastPassScan = set()
newPassScan = set()

def sendTextMessage(message):
    print("Preparing Text Message")
    messageText = client.messages \
                    .create(
                         body=message,
                         from_='+12029027334',
                         to=caseNum
                     )
    print("Text Message Sent")

def scrapeData():
    br = mechanize.Browser()
    print("Scraping...")
    response = br.open(store_url)
    print("Scraping Complete")
    print("Preparing Data...")
    data = response.read()
    return data

def parseData(oldSet, newSet):
    compare = newSet - oldSet
    if len(compare) > 0:
        for newVal in compare:
            sendTextMessage("New Update on SNKRS: " + newVal)
            print("New Item Added: " + newVal)
    else:
        print("No new items found, waiting until next scrape...")

def addShoeDataToSet(soupData):
    currentSet = set()
    i = 0
    while i < len(soupData):
        if (soupData[i].renderContents()[0].isalpha() and soupData[i].renderContents().find("WMNS") == -1):
            [shoeName, bleh] = soupData[i].renderContents().split("<")
            currentSet.add(shoeName)
        i += 1
    return currentSet

def addPassDataToSet(soupData):
    currentSet = set()
    i = 0
    while i < len(soupData):
        if (soupData[i].renderContents()[:2] == '<a'):
            theString = soupData[i].renderContents().split('aria-label="', 1)
            shoeString = theString[1].split('"', 1)
            if (snkrsPass in shoeString[0]):
                currentSet.add(shoeString[0])
        i += 1
    return currentSet

def main():
    print("Getting Inital Data...")
    initialData = scrapeData()
    daSoup = bs(initialData, features="html.parser")
    initialShoeNames = daSoup.findAll('h3', attrs = {"class": "ncss-brand"})
    intialPassNames = daSoup.findAll('div', attrs = {"class": "ncss-col-sm-12"})
    lastShoeScan = addShoeDataToSet(initialShoeNames)
    lastPassScan = addPassDataToSet(intialPassNames)

    while(1):
        print("Waiting on next scrape...")
        time.sleep(300)
        print("Getting New Data...")
        moreData = scrapeData()
        moreSoup = bs(moreData, features="html.parser")
        newShoeNames = moreSoup.findAll('h3', attrs = {"class": "ncss-brand"})
        newPassNames = moreSoup.findAll('div', attrs = {"class": "ncss-col-sm-12"})
        newShoeScan = addShoeDataToSet(newShoeNames)
        newPassScan = addPassDataToSet(newPassNames)
        parseData(lastShoeScan, newShoeScan)
        parseData(lastPassScan, newPassScan)
        if (len(newShoeScan) != 0):
            lastShoeScan = newShoeScan.copy()
        if (len(lastPassScan) != 0):
            lastPassScan = newPassScan.copy()

if __name__ == "__main__":
    main()
