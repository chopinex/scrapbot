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
from selenium.webdriver.support import expected_conditions as EC

dub = pd.read_csv('TB_UBIGEOS.csv', encoding='latin-1')

def fecha(cadena: str):
	entradas=cadena.split()
	#mapeo
	today=date.today()
	if entradas[-1] in ["Hoy","hoy"] :
		return today
	elif entradas[-1]=="ayer":
		return today-timedelta(days=1)
	elif entradas[-1]=="días":
		return today-timedelta(days=int(entradas[-2]))
	else:
		if entradas[-2]=="ene":
			return date(int(entradas[-1]),1,int(entradas[-3]))
		elif entradas[-2]=="feb":
			return date(int(entradas[-1]),2,int(entradas[-3]))
		elif entradas[-2]=="mar":
			return date(int(entradas[-1]),3,int(entradas[-3]))
		elif entradas[-2]=="abr":
			return date(int(entradas[-1]),4,int(entradas[-3]))
		elif entradas[-2]=="may":
			return date(int(entradas[-1]),5,int(entradas[-3]))
		elif entradas[-2]=="jun":
			return date(int(entradas[-1]),6,int(entradas[-3]))
		elif entradas[-2]=="jul":
			return date(int(entradas[-1]),7,int(entradas[-3]))
		elif entradas[-2]=="ago":
			return date(int(entradas[-1]),8,int(entradas[-3]))
		elif entradas[-2]=="sept":
			return date(int(entradas[-1]),9,int(entradas[-3]))
		elif entradas[-2]=="oct":
			return date(int(entradas[-1]),10,int(entradas[-3]))
		elif entradas[-2]=="nov":
			return date(int(entradas[-1]),11,int(entradas[-3]))
		elif entradas[-2]=="dic":
			return date(int(entradas[-1])-1,12,int(entradas[-3]))

def fecha2(cadena: str):
	entradas=cadena.split()
	if entradas[2]=="enero" or entradas[2]=="January":
		return date(int(entradas[4]),1,int(entradas[0]))
	elif entradas[2]=="febrero" or entradas[2]=="February":
		return date(int(entradas[4]),2,int(entradas[0]))
	elif entradas[2]=="marzo" or entradas[2]=="March":
		return date(int(entradas[4]),3,int(entradas[0]))
	elif entradas[2]=="abril" or entradas[2]=="April":
		return date(int(entradas[4]),4,int(entradas[0]))
	elif entradas[2]=="mayo" or entradas[2]=="May":
		return date(int(entradas[4]),5,int(entradas[0]))
	elif entradas[2]=="junio" or entradas[2]=="June":
		return date(int(entradas[4]),6,int(entradas[0]))
	elif entradas[2]=="julio" or entradas[2]=="July":
		return date(int(entradas[4]),7,int(entradas[0]))
	elif entradas[2]=="agosto" or entradas[2]=="August":
		return date(int(entradas[4]),8,int(entradas[0]))
	elif entradas[2]=="septiembre" or entradas[2]=="September":
		return date(int(entradas[4]),9,int(entradas[0]))
	elif entradas[2]=="octubre" or entradas[2]=="October":
		return date(int(entradas[4]),10,int(entradas[0]))
	elif entradas[2]=="noviembre" or entradas[2]=="November":
		return date(int(entradas[4]),11,int(entradas[0]))
	elif entradas[2]=="diciembre" or entradas[2]=="December":
		return date(int(entradas[4]),12,int(entradas[0]))

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

    depa=depa.replace("CHICLAYO","LAMBAYEQUE")
    depa=depa.replace("MAYNAS","LORETO")
    depa=depa.replace("ALTO AMAZONAS","LORETO")
    depa=depa.replace("SANTA","ANCASH")
    depa=depa.replace("LA MAR","AYACUCHO")

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

def get_ubigeo2(depa):
	replacements = (("Á","A"),("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),("ü", "u"))
	for (a,b) in replacements:
		depa=depa.replace(a,b)
	resultado=dub.loc[(dub['departamento']==depa.upper())]
	valor=resultado[['departamento_inei']].values.flatten().tolist()[0]
	return [int(valor),int(valor*100+1),int(valor*10000+101)]


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

def seleniumConfig():
	options=Options()
	service = Service(executable_path='./drivers/chromedriver')
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
	#options.add_argument(f'--proxy-server={proxy_server_url}')
	driver = webdriver.Chrome(service=service, options=options)
	return driver

def scroll_down(driver,howmany):
	if howmany<=30:
		return
	j = 0
	scrolls= (howmany-30)//10 + 1
	while j<scrolls:
		ele = WebDriverWait(driver,20).until(EC.visibility_of_element_located(('xpath','//div[contains(@class,"list__body")]')))
		driver.execute_script("arguments[0].scrollIntoView(true);", ele)
		time.sleep(0.5)
		#name = ele.find_element(By.XPATH, ".//descendant::h3//a").get_attribute('innerText')
		j = j + 1

def EPscrap(limit=""):
	limit=int(limit)
	#base_url="https://www.empleosperu.gob.pe/portal-mtpe/#/"
	base_url="https://mtpe-candidatos.empleosperu.gob.pe/search-jobs"
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	jobs=[]
	depas=[]
	distritos=[]
	desc=[]
	cats=[]
	date=[]
	date2=[]
	hipervinculos=[]
	newFound=0
	print("Capturando nuevos trabajos de mtpe-candidatos.empleosperu.gob.pe...")
	driver=seleniumConfig()
	driver.get(base_url)
	driver.implicitly_wait(5)
	#print(driver.page_source)
	#WebDriverWait(driver,30).until(EC.element_to_be_clickable(('xpath','//a[contains(@class,"btn-ofertas")]'))).click()
	scroll_down(driver,limit)
	ads=driver.find_elements('xpath','//a[contains(@class,"list__item")]')
	for a in ads[:limit]:
		newFound+=1
		jobs.append(a.find_element('xpath','.//h5').text)
		lugar=a.find_element('xpath','.//div[contains(@class,"vacancy__add-ellipsis")]').text.split("|")
		#print("Empresa - Sitio: ",lugar)
		if len(lugar)>1:
			lugar=lugar[1].split("-")
			#print("Depar - Dist: ",lugar)
			if len(lugar)>1:
				depas.append(lugar[0])
				distritos.append(lugar[1])
			else:
				depas.append("Lima")
				distritos.append("Lima")
		else:
			depas.append("Lima")
			distritos.append("Lima")
		hipervinculos.append(a.get_attribute("href"))
		nf=newFound//2
		sys.stdout.write("\r"+"*"*nf+" "+str(int(nf/limit*100))+"%")
		sys.stdout.flush()
		'''a.click()
		fecha=driver.find_element('xpath','.//div[contains(@class,"details-component__job-info")]')
		print(fecha.text)'''
	for h in hipervinculos:
		newFound+=1
		driver.get(h)
		time.sleep(2)

		try:
			fe=driver.find_element('xpath','//div[contains(@class,"details-component__job-info")]//li[contains(text(),"Fecha")]').text
		except:
			fe="hoy"
		date.append(fecha(fe))
		fe=driver.find_element('xpath','//div[contains(@class,"details-component__job-info")]//li[contains(text(),"Abierto")]').text
		date2.append(fecha(fe))
		desc.append(driver.find_element('xpath','//pre[contains(@class,"container")]//article').get_attribute("innerHTML"))
		nf=newFound//2
		sys.stdout.write("\r"+"*"*nf+" "+str(int(nf/limit*100))+"%")
		sys.stdout.flush()
		#print(description.get_attribute("innerHTML"))
	print()
	print(newFound//2," nuevos trabajos descubiertos")
	print("Iniciando procesamiento...")

	###dump in pandas
	df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
		"department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
		"validated","adtype_id","created_at"])

	for i in range(len(jobs)):
		dp=depas[i].strip()
		if dp.isdigit():
			ubigeo=[int(dp[:2]),int(dp),int(distritos[i])]
		else:
			ubigeo=get_ubigeo(dp,distritos[i].strip())
		#ubigeo=get_ubigeo(depas[i].strip(),distritos[i].strip())
		cats.append(mapa_categorias(jobs[i]+desc[i]))
		hasheo=get_random_string(7)
		slug=slugify(desc[i])
		objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
		'description':desc[i],'url':hipervinculos[i],'slug':slug+'-'+hasheo,'category_id':cats[i],
		'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':date[i],
		'date_to':date2[i],'imported':0,'date_created':date[i],'status':1,'validated':1,
		'adtype_id':1,'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		objeto = pd.DataFrame([objeto])
		df = pd.concat((df,objeto),ignore_index=True)
		time.sleep(0.1)
		sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
		sys.stdout.flush()
	print()
	print(df.shape[0]," trabajos agregados")
	return df

def PTscrap(limit=""):
	limit=int(limit)
	base_url='https://www.perutrabajos.com/'
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	r = requests.get(base_url,headers=HEADERS)
	print("Capturando nuevos trabajos de www.perutrabajos.com...")
	jobs=[]
	depas=[]
	#distritos=[]
	desc=[]
	cats=[]
	dates=[]
	hipervinculos=[]
	#ofertores=[]
	soup = BeautifulSoup(r.content, 'lxml')
	#print(soup)
	ads= soup.find_all('div',class_='post__content')
	newFound=0
	for a in ads:
		if newFound>=limit:
			break
		link1=a.find('a', href=True)
		r=requests.get(base_url+link1["href"],headers=HEADERS)
		soup = BeautifulSoup(r.content, 'lxml')
		empresa_desc=soup.find('div',class_='datos')
		empresa_desc=empresa_desc.text.split('\n')
		empresa_desc=[i for i in empresa_desc if i]
		empresa_desc='\n'.join(empresa_desc[1:-2])
		offers=soup.find_all('article',class_='info-conv')
		for of in offers:
			if newFound>=limit:
				break
			newFound+=1
			depa_txt='Departamento'
			fecha_txt='oferta'
			depa=of.find(lambda tag: tag.name == "p" and depa_txt in tag.text)
			if depa:
				ldt=depa.text.split()
				di=ldt.index("Departamento:") if "Departamento:" in ldt else -1
				pi=ldt.index("Provincia:")  if "Provincia:" in ldt else -1
				if pi>=0:
					depas.append(' '.join(ldt[di+1:pi])[:-1])
				else:
					depas.append(' '.join(ldt[di+1:]))
			else:
				depas.append("Lima")
			fechaa=of.find(lambda tag: tag.name == 'p' and fecha_txt in tag.text)
			if fechaa:
				dates.append(fecha2(' '.join(fechaa.text.split()[-5:])))
			else:
				dates.append(fecha2(date.today().strftime("%d de %B del %Y")))
			r=requests.get(base_url+of.h4.a["href"],headers=HEADERS)
			hipervinculos.append(base_url+of.h4.a["href"])
			soup = BeautifulSoup(r.content, 'lxml')
			title=soup.find('h1')
			jobs.append(title.text)
			description=soup.find('div',class_='conv-detalle')
			desc.append(empresa_desc+str(description.encode_contents()))
			sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
			sys.stdout.flush()
	print()
	print(newFound," nuevos trabajos descubiertos")
	print("Iniciando procesamiento...")

	###dump in pandas
	df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
		"department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
		"validated","adtype_id","created_at"])

	for i in range(len(jobs)):
		dp=depas[i].strip()
		'''if dp.isdigit():
			ubigeo=[int(dp[:2]),int(dp),int(distritos[i])]
		else:'''
		ubigeo=get_ubigeo2(dp)
		#ubigeo=get_ubigeo(depas[i].strip(),distritos[i].strip())
		cats.append(mapa_categorias(jobs[i]+desc[i]))
		hasheo=get_random_string(7)
		slug=slugify(desc[i])
		objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
		'description':desc[i],'url':hipervinculos[i],'slug':slug+'-'+hasheo,'category_id':cats[i],
		'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':date.today().strftime('%Y-%m-%d'),
		'date_to':dates[i],'imported':0,'date_created':date.today().strftime('%Y-%m-%d'),'status':1,'validated':1,
		'adtype_id':1,'created_at':date.today().strftime('%Y-%m-%d')}
		objeto = pd.DataFrame([objeto])
		df = pd.concat((df,objeto),ignore_index=True)
		time.sleep(0.1)
		sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
		sys.stdout.flush()
	print()
	print(df.shape[0]," trabajos agregados")
	return df

print(PTscrap("20"))
#EPscrap("10")