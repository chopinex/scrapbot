#!/var/www/myenv/bin/python3 -u
from selenium import webdriver
#from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd

#desired_capabilities = options.to_capabilities()
#executable_path='geckodriver'
#driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
#driver = webdriver.Firefox(desired_capabilities=desired_capabilities)
#driver.set_window_position(2000,0)
#driver.maximize_window()
#username = 'spweyay4hc'
#password = 'ur2xtC8aIhrb78nsQO'
#proxy_server_url = f"http://{username}:{password}@pe.smartproxy.com:40000"
options=Options()
#options=webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument(f'--proxy-server={proxy_server_url}')
options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
#driver=webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
#service = Service(executable_path='./drivers/geckodriver')
#driver=webdriver.Firefox(service=service,options=options)
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
service = Service(executable_path='./drivers/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)
driver.get('https://www.bumeran.com.pe/empleos/yt-grupo-analista-back-office-planeamiento-gestion-comercial-yatelnet-sac-1115930376.html')

'''
WebDriverWait(driver,5)\
    .until(EC.element_to_be_clickable((By.XPATH,
        '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div/div/li[2]/a/h2')))
'''
#time.sleep(60)
lugar=driver.find_element('xpath','//h1')
lugar=lugar.text
contenido=driver.find_element('xpath','//div[@id="section-detalle"]')
contenido=contenido.text
driver.close()
print(lugar)
print(contenido)
'''
lugar=driver.find_element('xpath','//div[@id="header-component"]')
#lugar=driver.find_element(By.ID,'header-component')
lugar=lugar.text
contenido=driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]')
#contenido=driver.find_element(By.ID,'section-detalle')
contenido=contenido.text
driver.quit()
print(lugar)
print(contenido)
'''    
