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

def TRDscrap(limit=""):
	limit=int(limit)
	axp=12
	totPags=limit//axp+1
	base_url='https://pe.trabajosdiarios.com/ofertas-trabajo?page='
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	
	print("Capturando nuevos trabajos de pe.trabajosdiarios.com...")
	jobs=[]
	depas=[]
	distritos=[]
	desc=[]
	cats=[]
	date=[]
	hipervinculos=[]
	newFound=0
	for pagina in range(1,totPags+1):
		urls=[]
		r = requests.get(base_url+str(pagina),headers=HEADERS)
		soup = BeautifulSoup(r.content, 'lxml')
		titles= soup.find_all('div',class_='font_3')
		texts=soup.find_all('div',class_='text-secondary')
		cards=soup.find_all('div',class_='card-body')
		if pagina*axp>limit:
			titles=titles[:limit-pagina*axp]
			texts=texts[:limit-pagina*axp]
			cards=cards[:limit-pagina*axp]
		for ss in titles:
			jobs.append(ss.text)
		for tt in texts:
			if len(tt.contents)>1:
				ttc=str(tt.contents[1])
				if ttc.find("bi-geo-alt")>0:
					ubi=tt.contents[2].text.split(",")
					depas.append(ubi[1])
					distritos.append(ubi[0])
		for cc in cards:
			c=cc.find_all('a',href=True)
			urls.append("https://pe.trabajosdiarios.com"+c[0].get('href'))
		for link in urls:
			r=requests.get(link,headers=HEADERS)
			soup=BeautifulSoup(r.content, 'lxml')
			s= soup.select("div.row.p-3.pt-1.pb-1")
			t= soup.select("div.row.p-3.pt-1.pb-3")
			desc.append(s[0].encode_contents()+t[0].encode_contents())
			f=soup.select("div.col.mb-3.mt-0.ms-2.ps-3.pt-0.texto_azul")
			date.append(fecha(f[0].text))
			newFound+=1
			sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
			sys.stdout.flush()
		hipervinculos=hipervinculos+urls
		if newFound>=limit:
			break
	print()
	print(newFound," nuevos trabajos descubiertos")
	print("Iniciando procesamiento...")

	###dump in pandas
	df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
		"department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
		"validated","adtype_id","created_at"])

	for i in range(len(jobs)):
		ubigeo=get_ubigeo(depas[i].strip(),distritos[i].strip())
		cats.append(mapa_categorias(jobs[i]+desc[i].decode('utf-8')))
		#print(depas[i]+" "+distritos[i]+" "+str(ubigeo))
		if len(ubigeo)>=3:
			sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
			sys.stdout.flush()
			hasheo=get_random_string(7)
			slug=slugify(desc[i])
			objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
			'description':desc[i],'url':hipervinculos[i],'slug':slug+'-'+hasheo,'category_id':cats[i],
			'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':date[i],
			'date_to':date[i]+timedelta(days=30),'imported':0,'date_created':date[i],'status':1,'validated':1,
			'adtype_id':1,'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
			objeto = pd.DataFrame([objeto])
			df = pd.concat((df,objeto),ignore_index=True)
			time.sleep(0.1)
			sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
			sys.stdout.flush()
	print()
	print(df.shape[0]," trabajos agregados")
	return df

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

	options=Options()
	service = Service(executable_path='./drivers/chromedriver')
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
	driver = webdriver.Chrome(service=service, options=options)
	###Ciclo?
	page_url=base_url+regiones[0]+"&start=0"
	driver.get(page_url)
	for j in range(totPags[0]):
		#print(driver.current_url)
		titulos=driver.find_elements('xpath','//h2[contains(@class, "jobTitle")]//a')
		lugares=driver.find_elements('xpath','//div[contains(@class,"companyLocation")]')
		tiempos=driver.find_elements('xpath','//div[contains(@class,"heading6")]//span[@class="date"]')
		if (j+1)*axp>limites[0]:
			titulos=titulos[:limites[0]-j*axp]
			lugares=lugares[:limites[0]-j*axp]
			tiempos=tiempos[:limites[0]-j*axp]
		for t in titulos:
			jobs.append(t.text)
			#print(t.get_attribute("href"))
			#iden=t.get_attribute("id")
			#iden=iden.replace("job_","")
			hipervinculos.append(t.get_attribute("href"))
			#t.click()
		for l in lugares:
			ll=re.split(',|\n',l.text)
			if len(ll)<2:
				distritos.append(regiones[0])
				depas.append(regiones[0])
			else:
				distritos.append(ll[0])
				depas.append(ll[1])
		for tt in tiempos:
			ttt=tt.text.replace("Posted\n","")
			print(ttt)
			date.append(fecha(ttt))
		nexts=driver.find_elements('xpath','//a[contains(@class,"css-akkh0a")]')
		print(nexts[-1].get_attribute("href"))
		driver.implicitly_wait(15)
		nexts[-1].click()
	print(len(jobs))
	for h in hipervinculos:
		driver.get(h)
		descripcion=driver.find_element('xpath','//div[@id="jobDescriptionText"]')
		desc.append(descripcion.get_attribute('innerHTML'))
	print(len(desc))
#INscrap("20")

