import socket
import logging
import subprocess
import time
import os
from decouple import config
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


criteria = config('SEARCH_CRITERIA')
base_search_URL = 'https://www.linkedin.com/search/results/people/?geoUrn=%5B%22106057199%22%5D&keywords='
pages = config('PAGES')
message = config('MESSAGE')


def killAll():
    subprocess.call("TASKKILL /f  /IM  CHROME.EXE")
    subprocess.call("TASKKILL /f  /IM  CHROMEDRIVER.EXE")

def initDrivers():
    try:
        options = webdriver.ChromeOptions() # Chrome options
        options.add_argument('lang=pt-br')
        options.add_experimental_option("detach", True) # Setting to chrome to not kill it self on the end of the run

        chrome_options = options  
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options) #Here is where the chrome plugin download the last version
        return driver
    except:
        return()

def login(driver):
    driver.get('https://www.linkedin.com/')
    driver.maximize_window()
    driver.find_element_by_name("session_key").send_keys(config('LINKEDIN_USER'))
    driver.find_element_by_name("session_password").send_keys(config('LINKEDIN_PASS') + Keys.ENTER)

def search(driver, criteria, urlSearch):
    quote = criteria.split(' ')

    for word in quote:
        urlSearch += word + '%20'
    urlSearch += "&origin=GLOBAL_SEARCH_HEADER"
    driver.get(urlSearch)

    return urlSearch

def scraper(driver, url, pages, message):
    
    pageNumber=0

    for l in range(int(pages)):
            #personsURL = driver.find_elements_by_class_name('app-aware-link') #get url
            #personsURL = [y.get_attribute('href') for y in personsURL]
            #personsURL = list(dict.fromkeys(personsURL)) #remove duplicates

            #for personURL in personsURL:
            #    print(personURL)

            time.sleep(3)

            buttonsList = []
            nameList = []

            everyName = driver.find_elements_by_tag_name("span") #get persons name
            everyName = [s for s in everyName if s.get_attribute("aria-hidden") == "true"]
            del everyName[-1]
            idx = len(everyName)


            everyButton = driver.find_elements_by_tag_name("button")
            
            for btn in everyButton:
                if btn.text == "Enviar mensagem" or btn.text == "Conectar":
                    buttonsList.append(btn)


            for i in range(len(everyName)):
                name = everyName[i].text.split(" ")[0]
                if name:
                    nameList.append(name)

            
            if len(nameList) == len(buttonsList):
                for k in range(len(nameList)):

                    if buttonsList[k].text == "Enviar mensagem":
                        driver.execute_script("arguments[0].click();", buttonsList[k])
                        nameIndex = nameList[k]

                        sendMessage(driver, nameIndex, message)

        
            pageNumber = pageNumber+1

            if pageNumber == 1:
                pageNumber=pageNumber+1
            
            driver.get(url+"&page="+str(pageNumber))
    

def sendMessage(driver, name, message):
    

    paragraphs = driver.find_elements_by_tag_name("p")
    paragraphs[-5].send_keys("Olá "+name+" "+message)

    time.sleep(2)

    driver.find_element_by_class_name('msg-form__send-button').click()

    time.sleep(2)

    buttons = driver.find_elements_by_tag_name("button")
    buttons = [s for s in buttons if s.get_attribute("data-control-name") == "overlay.close_conversation_window"]

    buttons[0].click()



def sendMessageProfile(driver):

    time.sleep(5)

    driver.find_element_by_class_name('message-anywhere-button').click() #send message on the profile

    time.sleep(2)

    paragraphs = driver.find_elements_by_tag_name("p")
    paragraphs[-5].send_keys("msg")

    time.sleep(2)

    driver.find_element_by_class_name('msg-form__send-button').click()

    time.sleep(2)
    driver.find_element_by_id('ember305').click() #close message


killAll()

Driver_values = initDrivers()

login(Driver_values)

url = search(Driver_values, criteria, base_search_URL)

scraper(Driver_values,url,pages,message)
