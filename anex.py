import requests
from bs4 import BeautifulSoup
from datetime import date,timedelta,datetime
import sys
import pandas as pd
import random
import time
from complements import slugify, get_random_string
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

dub = pd.read_csv('TB_UBIGEOS.csv', encoding='latin-1')

def fecha(cadena: str):
    entradas=cadena.split()
    #mapeo
    today=date.today()
    if entradas[-1] == "hoy":
        return today
    elif entradas[-1]=="ayer":
        return today-timedelta(days=1)
    elif entradas[-1]=="días":
        return today-timedelta(days=int(entradas[-2]))

def get_ubigeo(depa,dist):
    dist=dist.replace("Cercado De ","")
    dist=dist.replace("CENTRO DE ","")
    dist=dist.replace(" vitarte","")
    dist=dist.replace("Aguaytía","Padre Abad")
    dist=dist.replace("Chosica","Lurigancho")
    dist=dist.replace("Pucallpa","Calleria")
    dist=dist.replace("Distrito de ","")
    dist=dist.replace(" Cercado","")
    dist=dist.replace("Urb. Maranga - ","")
    dist=dist.replace(".","")
    dist=dist.replace(" - Lima","")
    replacements = (("Á","A"),("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),("ü", "u"))
    for (a,b) in replacements:
      dist=dist.replace(a,b)
      depa=depa.replace(a,b)
    if dist=="Magdalena":
        dist="Magdalena del Mar"
    if dist=="Callao":
        depa="Callao"
    resultado=dub.loc[(dub['departamento']==depa.upper()) & (dub['distrito']==dist.upper())]
    lista=resultado[['departamento_inei','provincia_inei','ubigeo_inei']].values.flatten().tolist()
    return list(map(int,lista))

def mapa_categorias(text):
	clean = re.compile(r'<.*?>')
	text = re.sub(clean,'',text)
	text=text.lower()
	if text.find('admin') > -1:
		return 2
	if text.find('almac') > -1:
		return 82
	if text.find('chofer') + text.find('motor') + text.find('transpor') > -3:
		return 4
	if text.find('call') > -1:
		return 5
	if text.find('comunic') > -1:
		return 8
	if text.find('contab') > -1:
		return 10
	if text.find('diseñ') > -1:
		return 12
	if text.find('docent') + text.find('capacit') > -2:
		return 13
	if text.find('cocin') + text.find('hotel') + text.find('host') > -3:
		return 14
	if text.find('compu') + text.find('web') + text.find('frontend') + text.find('backend') > -4:
		return 16
	if text.find('derecho') + text.find('legal') > -2:
		return 20
	if text.find('mina') + text.find('geo') > -2:
		return 23
	if text.find('medic') + text.find('enfer') + text.find('farma') > -3:
		return 27
	if text.find('credit') + text.find('presta') > -2:
		return 44
	if text.find('veter') + text.find('mascot') > -2:
		return 54
	if text.find('electr') > -1:
		return 48
	if text.find('constru') + text.find('civil') + text.find('arqui') > -3:
		return 27
	if text.find('social') > -1:
		return 96
	if text.find('vend') + text.find('vent') > -2:
		return 6
	if text.find('geren') > -1:
		return 11
	if text.find('ingenie') > -1:
		return 17
	if text.find('market') > -1:
		return 22
	if text.find('produc') > -1:
		return 24
	if text.find('reclut') + text.find('human') > -2:
		return 25
	if text.find('preven') + text.find('segur') > -2:
		return 29
	if text.find('serv') + text.find('limp') > -2:
		return 30
	if text.find('compr') > -1:
		return 56
	if text.find('operac') > -1:
		return 87
	return 34

def INscrap(limit=""):
	limites=limit.split(",")
	limites = list(map(int,limites))
	#total=sum(limites)
	axp=15
	regiones=["Lima","Arequipa","Cusco","La Libertad"]
	totPags=[lim//axp+1 for lim in limites]
	base_url='https://pe.indeed.com/jobs?q=&l='
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	jobs=[]
	depas=[]
	distritos=[]
	desc=[]
	cats=[]
	date=[]
	hipervinculos=[]
	print("Capturando nuevos trabajos de pe.indeed.com...")

	username = 'spweyay4hc'
	password = 'ur2xtC8aIhrb78nsQO'
	proxy_server_url = f"http://{username}:{password}@pe.smartproxy.com:40000"
	options=Options()
	service = Service(executable_path='./drivers/chromedriver')
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
	#options.add_argument(f'--proxy-server={proxy_server_url}')
	driver = webdriver.Chrome(service=service, options=options)
	for i in range(len(regiones)):
		page_url=base_url+regiones[i]+"&start=0"
		driver.get(page_url)
		print(page_url)
		for j in range(totPags[i]):
			titulos=driver.find_elements('xpath','//h2[contains(@class, "jobTitle")]//a')
			lugares=driver.find_elements('xpath','//div[contains(@class,"companyLocation")]')
			tiempos=driver.find_elements('xpath','//div[contains(@class,"heading6")]//span[@class="date"]')
			if (j+1)*axp>limites[i]:
				titulos=titulos[:limites[i]-j*axp]
				lugares=lugares[:limites[i]-j*axp]
				tiempos=tiempos[:limites[i]-j*axp]
			for t in titulos:
				jobs.append(t.text)
				#print(t.get_attribute("href"))
				#iden=t.get_attribute("href")
				#iden=iden.replace("job_","")
				hipervinculos.append(t.get_attribute("href"))
				#driver.implicitly_wait(15)
				#driver.execute_script("arguments[0].click();", iden)
				#iden.click()
				#descripcion=driver.find_element('xpath','//div[@id="jobDescriptionText"]')
				#desc.append(descripcion.get_attribute('innerHTML'))
			for l in lugares:
				ll=re.split(',|\n',l.text)
				if len(ll)<2:
					distritos.append(regiones[i])
					depas.append(regiones[i])
				else:
					distritos.append(ll[0])
					depas.append(ll[1])
			for tt in tiempos:
				ttt=tt.text.replace("Posted\n","")
				if len(ttt)<3:
					date.append("hoy")
				else:
					date.append(fecha(ttt))
			nexts=driver.find_elements('xpath','//a[contains(@class,"css-akkh0a")]')
			print(nexts[-1].get_attribute("href"))
			driver.implicitly_wait(15)
			#nexts[-1].click()
			driver.execute_script("arguments[0].click();", nexts[-1])
		print(len(desc))
		for h in hipervinculos:
			driver.implicitly_wait(15)
			driver.get(h)
			descripcion=driver.find_element('xpath','//div[@id="jobDescriptionText"]')
			desc.append(descripcion.get_attribute('innerHTML'))
INscrap("10,10,10,10")