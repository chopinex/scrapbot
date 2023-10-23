import requests
from bs4 import BeautifulSoup
from datetime import date,timedelta,datetime
import sys
import pandas as pd
import random
import time
from complements import slugify, get_random_string, basicHash, envioEmpresas
from lxml import html, etree
import re
import math

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
	if entradas[-1] == "antes":
		entradas.pop()
	today=date.today()
	if entradas[-1] in ["Hoy","hoy","hrs"] :
		return today
	elif entradas[-1]=="ayer":
		return today-timedelta(days=1)
	elif entradas[-1] in ["días","dias"]:
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
		j = j + 11

def TRMscrap(limit=""):
	limit=int(limit)
	totalxp=20
	numpags=math.ceil(limit/totalxp)
	base_url='https://www.troomes.com/ucp.php?mode=login'
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	print("Capturando nuevos trabajos de www.troomes.com...")
	jobs=[]
	depas=[]
	#distritos=[]
	desc=[]
	cats=[]
	dates=[]
	hipervinculos=[]
	newFound=0
	session = requests.Session()
	login=session.get(base_url,headers=HEADERS)
	parser = html.fromstring(login.text)
	ses_token=parser.xpath('//input[@name="form_token"]/@value')
	ses_id=parser.xpath('//input[@name="sid"]/@value')
	ses_time=parser.xpath('//input[@name="creation_time"]/@value')
	login_data={
		"username": "arturoAqp",
		"password": "Gamer001!",
		"form_token": ses_token,
		"sid": ses_id,
		"redirect": "./index.php",
		"creation_time": ses_time
	}
	session.post(base_url,data=login_data,headers=HEADERS)
	data_url="https://www.troomes.com/app.php/postulante/busqueda?page="
	for j in range(numpags):
		if newFound>=limit:
			break
		respuesta=session.get(data_url+str(totalxp*j),headers=HEADERS)
		parser = html.fromstring(respuesta.text)
		titulos=parser.xpath('//div[@class="listempleos"]//b[@class="titulo_oferta"]/text()')
		fechas=parser.xpath('//div[@class="listempleos"]/span[3]/text()')
		lugares=parser.xpath('//div[@class="listempleos"]//span[4]/text()')
		ofertas=parser.xpath('//button[@class="Btnresultados"]/@value')
		for i in range(totalxp):
			newFound+=1
			sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
			sys.stdout.flush()
			jobs.append(titulos[i])
			dates.append(fecha(fechas[i]))
			depas.append(lugares[i])
			search_data={
				"mode":"mostrar_oferta",
				"id_oferta":ofertas[i]
			}
			buscar=session.post(data_url,data=search_data,headers=HEADERS)
			parser = html.fromstring(buscar.text)
			descripcion=parser.xpath('//div[@id="oferta_trabajo"]/div[@class="descripcion"]')
			for d in descripcion:
				desc.append(etree.tostring(d,encoding='unicode'))
			job_url="https://www.troomes.com/app.php/jobs/"
			hipervinculos.append(job_url+ofertas[i])
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
		'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':dates[i],
		'date_to':dates[i]+timedelta(days=30),'imported':0,'date_created':dates[i],'status':1,'validated':1,
		'adtype_id':1,'created_at':date.today().strftime('%Y-%m-%d')}
		objeto = pd.DataFrame([objeto])
		df = pd.concat((df,objeto),ignore_index=True)
		time.sleep(0.1)
		sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
		sys.stdout.flush()
	print()
	print(df.shape[0]," trabajos agregados")
	return df

def envio(send_data):
	send_url="https://oflik.pe/api/add/ad"
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	respuesta=requests.post(send_url,data=send_data,headers=HEADERS)
	print(respuesta.text)

def LINscrap(limit="10"):
	limit=int(limit)
	tope=25
	j=0
	newFound=0
	base_url='https://www.linkedin.com/jobs/search?keywords=&location=Peru&geoId=&trk=guest_homepage-basic_guest_nav_menu_jobs'
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	print("Capturando nuevos trabajos de pe.linkedin.com...")
	enlaces=[]
	jobs=[]
	hipervinculos=[]
	ubicaciones=[]
	emps=[]
	descripciones=[]
	empresas={}
	driver=seleniumConfig()
	driver.get(base_url+"&position=1&pageNum=0")
	driver.implicitly_wait(5)
	while (tope*j)//limit<1:
		driver.get('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location=Peru&geoId=&trk=guest_homepage-basic_guest_nav_menu_jobs&start='+str(j*tope))
		links=driver.find_elements('xpath','//a[contains(@class,"base-card__full-link")]')
		for l in links:
			if newFound>=limit:
				break
			newFound+=1
			enlaces.append(l.get_attribute('href'))
		j+=1
	for e in enlaces:
		pos=e.find("?")
		hrefer="https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"+e[pos-10:pos]
		hipervinculos.append(hrefer)
		#t = requests.get(hrefer,headers=HEADERS)
		#soup = BeautifulSoup(t.content, 'lxml')
		driver.get(hrefer)
		print(driver.page_source)
		#title=soup.find('h2',class_="top-card-layout__title")
		title=driver.find_element('xpath','//h2[contains(@class,"top-card-layout__title")]')
		jobs.append(title)
		#ubicaciones.append(soup.find('span',class_="topcard__flavor--bullet").text)
		ubi=driver.find_element('xpath','//span[contains(@class,"topcard__flavor--bullet")]')
		ubicaciones.append(ubi.text)
		#ee=soup.find('a',class_="topcard__org-name-link").text
		ee=driver.find_element('xpath','//a[contains(@class,"topcard__org-name-link")]')
		ee=ee.text
		emps.append(ee)
		bh=basicHash(ee)%101
		if bh in empresas.keys():
			if ee not in empresas[bh]:
				empresas[bh].append(ee)
				datos_empresas={'name':ee}
				#,'image':img_emp
				envioEmpresas(datos_empresas)
			else:
				empresas[bh]=[]
				empresas[bh].append(ee)
				datos_empresas={'name':ee}
				envioEmpresas(datos_empresas)
		#descripciones.append(soup.find("div",class_="show-more-less-html__markup").encode_contents())
		desc=driver.find_element('xpath','//div[contains(@class,"show-more-less-html__markup")]')
		descripciones.append(desc.get_attribute('innerHtml'))
		time.sleep(1)
	print(jobs)
	print(ubicaciones)
	print(emps)
	print(empresas)
	#print(descripciones)

def retries(url,headers,proxy):
	MAX_RETRIES=3
	for _ in range(MAX_RETRIES):
		try:
			r = requests.get(url,headers=headers, proxies = {
			'http': proxy,
			'https': proxy
			}, timeout=(30,60))
			if r.status_code in [200, 404]:
				break
		except requests.exceptions.ConnectTimeout:
			pass
		except requests.exceptions.SSLError:
			pass
		except requests.exceptions.ProxyError:
			pass
	if r is None or r.status_code != 200:
		print('Request has timed out')
		return
	else:
		return r

def ubicania():
	base_url="https://ubicania.com/"
	send_url="https://staging.oflik.pe/api/add/company"
	HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	username = 'spweyay4hc'
	password = 'ur2xtC8aIhrb78nsQO'
	proxy = f"http://{username}:{password}@pe.smartproxy.com:40000"
	r = requests.get(base_url,headers=HEADERS)
	soup = BeautifulSoup(r.content, 'html.parser')
	depas = soup.find_all('a',class_='blue')
	#for d in depas:
	#	print(d['href'])
	r=retries(base_url+depas[1]['href'],HEADERS,proxy)
	#r = requests.get(base_url+depas[0]['href'])
	soup = BeautifulSoup(r.content, 'html.parser')
	ads=soup.find_all('div',class_='item_list')
	for ad in ads:
		emp_url=ad.div.next_sibling.next_sibling.span.a['href']
		r=retries(emp_url,HEADERS,proxy)
		soup = BeautifulSoup(r.content, 'html.parser')
		titulo=soup.find('h1').text
		direccion=soup.find_all('div',class_='info_block')
		direccion=direccion[0].text.split(':')[1]
		ruc=soup.find('div',class_='product_description')
		ruc=ruc.ul.li.text.split(':')[1]
		datos_empresas={'name':titulo,'ruc':ruc.strip(),'address':direccion.strip()}
		#print(titulo,ruc.strip(),direccion.strip())
		respuesta=requests.post(send_url,data=datos_empresas,headers=HEADERS)
		print(respuesta.text)
ubicania()
