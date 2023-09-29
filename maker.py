import urllib

from PIL.PngImagePlugin import PngInfo
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import os.path
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import urllib.request
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import base64
import csv
import random
from itertools import accumulate
##import pandas as pd  -- Pandas doesnt fuking work err as ValueError: bad marshal data (unknown type code)

siteName = 'https://deepai.org/chat'
timeout = 10

##Opens and reads dictionaries
nd = open('initials.csv', 'r')
readerName = csv.reader(nd)
cd = open('classes.csv', 'r')
readerClass = csv.reader(cd)
rd = open("races.csv", 'r')
readerRace = csv.reader(rd)

##Assigns CSVs to dictionaries
namedict = dict(enumerate(readerName))
classdict = dict(enumerate(readerClass))
racedict = dict(enumerate(readerRace))

## this stores the whole list in memory but without working panda is the only way
## df = pd.read_csv('initials.csv') ##data frame alternative for pandas

##Size of Axis X for dictionaries
def rowcnt(atr):
    if atr == 'nd':
        return (sum(1 for x in namedict)-1)
    elif atr == 'cd':
        return (sum(1 for row in classdict)-1)
    elif atr == 'rd':
        return (sum(1 for row in racedict)-1)
    else:
        return 'err'

##Assign attributes of name, class, and race to character
def get_attr(atr):
    if atr == nd:
        return namedict[random.randint(0, rowcnt('nd'))][1]
    elif atr == cd:
        return classdict[random.randint(1, rowcnt('cd'))][0]
    elif atr == rd:
        return racedict[random.randint(0, rowcnt('rd'))][0]
    else:
        return 'err'

def waittill(type, identity):  ## probably way more clunky than just adding driver.implicitly_wait(10) every time but eh
    try:
        if type == "ID":
            return WebDriverWait(browser, timeout).until(EC.presence_of_element_located(('id', identity)))
        elif type == "class":
            return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, identity)))
        elif type == "tag":
            return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.TAG_NAME, identity)))
        elif type == "name":
            return WebDriverWait(browser, timeout).until(EC.presence_of_element_located(("name", identity)))
        else:
            print("Element type unexpected")
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")


## Begin querey to the Deep AI, creates base question
question = ("Describe the appearance and demeanor of a DND character that looks like " + get_attr(nd) + " yet is a " + get_attr(rd) + " who works as a " + get_attr(cd))

nd.close()
cd.close()
rd.close()

## opening browser and site
opts = Options()
opts.headless = False
#assert opts.headless  # operating in headless mode
#driver = webdriver.Firefox(options=opts) # for use with the gekodrier
#driver.get(siteName)
browser = Firefox(options=opts)
browser.get(siteName)
driver = browser

## Poses Question to define character then takes detailed description as result
#waittill("class", "chatbox") ## Unfortunatly have to wait to load 6+ ads ,, waits too long idk why
search_form = browser.find_element(By.CLASS_NAME,"chatbox")
go_button = browser.find_element(By.ID,"chatSubmitButton")


search_form.send_keys(question)


#browser.switch_to.frame(0)
#go_button.click() also doesnt work
#browser.find_element(By.CLASS_NAME,"chatbox").submit()   ##WHY DOESNT THIS WORK  -> To submit an element, it must be nested inside a form element
browser.find_element(By.CLASS_NAME,"chatbox").send_keys(Keys.ENTER)
waittill("class", 'outputbox')
results = browser.find_element(By.CLASS_NAME,'outputBox').text
#results = driver.find_elements(By.CLASS_NAME, "results")
#results = driver.find_elements_by_id ("outputBox")


##Second phase, New site via browser, Queries new AI using Results
##siteName = "https://perchance.org/ai-character-generator"   perchance doesnt work due to hyphens in input boxes
siteName = "https://www.artguru.ai/"
browser.get(siteName)
browser.implicitly_wait(timeout)
#browser.switch_to.frame(browser.find_element(By.TAG_NAME, 'iframe'))
#search_form = browser.find_element(By.CSS_SELECTOR, 'textarea[class*="paragraph"][class*="input"]')  ## for perchance textarea.paragraph-input for css selector but hyphen breaks it
search_form = browser.find_element(By.TAG_NAME, "textarea")
search_form.click()
search_form.send_keys(results)
browser.find_element(By.CSS_SELECTOR, '[class*="btn-generate"]').click()
#search_form.send_keys(Keys.ENTER)

img_list = []
browser.implicitly_wait(30)
imgObj = browser.find_elements(By.TAG_NAME,'img')[16] ##commits the image id to an object
#pic = Image.open(BytesIO(base64.b64decode(imgObj))) #base64 encoding and load into memory double step, probably the most expensive step
pic = imgObj.get_attribute('src')
# First pic was the open image itself, now its the URL to the image for simplicity

# Wait for image to load before capturing data
element_present = waittill("tag", 'img')
##adds the question from the last section to the metadata of the image
path = 'C:\\Users\\Johnsi3\\Pictures\\forFather'
urllib.request.urlretrieve(pic, "{}\\{}_{}.jpg".format(path, get_attr(nd), get_attr(cd)))
#                                     image URL , path with image named after qualia
## Trying to modify the metadata directly to add the resolved description
#imgObj.new_attr = "{}".format(results)

targetImage = Image.open(path + "{}\\{}_{}.jpg".format(path, get_attr(nd), get_attr(cd)))
metadata = PngInfo()
metadata.add_text("Result info", results)
metadata.add_text("Question key", question)
targetImage.save(path + "{}\\{}_{}.jpg".format(path, get_attr(nd), get_attr(cd)), pnginfo=metadata)


print(results)


#Next Step is to reenter the question with specific items added in https://www.artguru.ai/ doesnt have an Add Element feature so this would require resizing the prompt question
