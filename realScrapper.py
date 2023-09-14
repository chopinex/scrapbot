#!/var/www/myenv/bin/python3 -u
import requests
from bs4 import BeautifulSoup,SoupStrainer
from mysql.connector import connect, Error
import sqlite3
from sqlalchemy import create_engine
from timeloop import Timeloop
from datetime import date,timedelta,datetime
import random
import string
import sys
from urllib import parse
from complements import descripcion, slugify, categoria, categoriaB, get_random_string
from anexScrapper import TRDscrap
from threading import Thread
import pandas as pd
import math
import time
from selenium import webdriver
#from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import numpy as np

dub = pd.read_csv('TB_UBIGEOS.csv', encoding='latin-1')

def hash(cadena: str):
    p=31
    m=10**9+7
    hsh=0
    largo=len(cadena)
    for i in range(largo):
        hsh+=ord(cadena[i])*p**i
    return hsh % m

def fecha(cadena: str):
    entradas=cadena.split()
    #mapeo
    today=date.today()
    if entradas[-1] in ["Ahora","minutos","horas","minuto","hora"]:
        return today
    elif entradas[-1]=="Ayer":
        return today-timedelta(days=1)
    elif entradas[-1]=="días":
        return today-timedelta(days=int(entradas[-2]))
    else:
        if entradas[-1]=="enero":
            return date(today.year,1,int(entradas[0]))
        elif entradas[-1]=="febrero":
            return date(today.year,2,int(entradas[0]))
        elif entradas[-1]=="marzo":
            return date(today.year,3,int(entradas[0]))
        elif entradas[-1]=="abril":
            return date(today.year,4,int(entradas[0]))
        elif entradas[-1]=="mayo":
            return date(today.year,5,int(entradas[0]))
        elif entradas[-1]=="junio":
            return date(today.year,6,int(entradas[0]))
        elif entradas[-1]=="julio":
            return date(today.year,7,int(entradas[0]))
        elif entradas[-1]=="agosto":
            return date(today.year,8,int(entradas[0]))
        elif entradas[-1]=="setiembre":
            return date(today.year,9,int(entradas[0]))
        elif entradas[-1]=="octubre":
            return date(today.year,10,int(entradas[0]))
        elif entradas[-1]=="noviembre":
            return date(today.year,11,int(entradas[0]))
        elif entradas[-1]=="diciembre":
            return date(today.year-1,12,int(entradas[0]))

def extraer(test_list, vals):
    for ele in test_list:
        if ele in vals:
            return
        yield ele

def get_ubigeo(depa,dist):
    dist=dist.replace("Cercado De ","")
    dist=dist.replace("Aguaytía","Padre Abad")
    dist=dist.replace("Chosica","Lurigancho")
    dist=dist.replace("Pucallpa","Calleria")
    dist=dist.replace("Distrito de ","")
    dist=dist.replace(" Cercado","")
    dist=dist.replace("Urb. Maranga - ","")
    dist=dist.replace(".","")
    dist=dist.replace(" - Lima","")
    replacements = (("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),("ü", "u"))
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
    
def CTscrap(limit=""):
    print("Capturando nuevos trabajos de pe.computrabajo.com...")
    base_url='https://pe.computrabajo.com'
    # Making a GET request
    #HEADERS = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
    HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    username = 'spweyay4hc'
    password = 'ur2xtC8aIhrb78nsQO'
    proxy = f"http://{username}:{password}@pe.smartproxy.com:40000"
    MAX_RETRIES=3
    for _ in range(MAX_RETRIES):
        try:
            r = requests.get(base_url,headers=HEADERS, proxies = {
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
    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    s= soup.find_all('ul',class_='lS')
    #s= soup.find_all('div',class_='hide')
    content=[]
    for tags in s:
        content=content + tags.find_all('a',href=True)
    endpoints=[]
    limites=limit.split(",")
    limites = list(map(int,limites))
    total=sum(limites)
    incremento=90/total
    lugares=["lima","arequipa","callao","libertad","piura","ica","lambayeque","cusco","junin","ancash","cajamarca","puno"]
    ubi = dict(zip(lugares, limites))
    for link in content:
        hyper=link.get('href')
        for lug in lugares:
            if lug in hyper and ubi[lug]:
                endpoints.append(hyper)
    jobs=[]
    depas=[]
    distritos=[]
    dates=[]
    cat=[]
    colisiones=[]
    newFound=0
    desc=[]
    hipervinculos=[]
    ll=sum(ubi.values())
    #npi=0
    for ep in endpoints:
        donde=""
        for i,lug in enumerate(lugares):
            if lug in ep:
                donde=lug
                break
        if ubi[donde]==0:
            continue
        ss=[]
        for i in range(1,6):
            proxy=f"http://{username}:{password}@pe.smartproxy.com:40000"
            for _ in range(MAX_RETRIES):
                try:
                    r = requests.get(base_url+ep+"?p="+str(i),headers=HEADERS, proxies = {
                    'http': proxy,
                    'https': proxy
                    }, timeout=(30,60))
                    if r.status_code in [200, 404]:
                        break
                except requests.ConnectTimeout:
                    pass
                except requests.exceptions.SSLError:
                    pass
                except requests.exceptions.ProxyError:
                    pass
            if r is None or r.status_code != 200:
                print('Request has timed out')
                return
            soup = BeautifulSoup(r.content, 'html.parser')
            sous=soup.find_all('article')
            ss=ss+sous
        for link in ss:
            dt=link.find_all('p',class_="fs13")[0].text
            pl=''.join(link.find_all('p',class_='fs16')[0].find_all(recursive=False,string=True)).strip()
            words=pl.split(", ")
            #print(words)
            if len(words)<2:
                words.append(words[0])
            ltw=words[-2].split()
            txt=link.get('id')
            jb=link.find_all('h2')[0].text
            url=base_url+ep+"#"+txt
            #code=hash(jb+ltw[-1]+","+words[-1])
            if txt not in colisiones:
                if ubi[donde]:
                    jobs.append(jb)
                    if ltw[-1]=="Libertad":
                        depas.append("La "+ltw[-1])
                    else:
                        depas.append(ltw[-1])
                    distritos.append(words[-1])
                    dates.append(fecha(dt))
                    #colisiones[code]=[]
                    colisiones.append(txt)
                    dtxt=descripcion(txt)
                    desc.append(dtxt)
                    hipervinculos.append(url)
                    cat.append(categoria(dtxt))
                    ubi[donde]-=1
                    #np[lug]=math.ceil((limites[i]-ubi[donde])/20)
                    newFound+=1
                    sys.stdout.write("\r"+"*"*int(newFound*incremento)+" "+str(int(newFound/total*100))+"%")
                    sys.stdout.flush()
                    time.sleep(0.1)
                else:
                    break
    ###dump in pandas
    df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
        "department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
        "validated","adtype_id","created_at"])
    print()
    print(newFound," nuevos trabajos descubiertos")
    print("Iniciando procesamiento...")
    for i in range(len(jobs)):
        ubigeo=get_ubigeo(depas[i],distritos[i])
        #print(ubigeo)
        if len(ubigeo)>=3:
            sys.stdout.write("\r"+"*"*int((i+1)*incremento)+" "+str(int((i+1)/len(jobs)*100))+"%")
            sys.stdout.flush()
            hasheo=get_random_string(7)
            slug=slugify(desc[i])
            objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
            'description':desc[i],'url':hipervinculos[i],'slug':slug+'-'+hasheo,'category_id':cat[i],
            'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':dates[i],
            'date_to':dates[i]+timedelta(days=30),'imported':0,'date_created':dates[i],'status':1,'validated':1,
            'adtype_id':1,'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            objeto = pd.DataFrame([objeto])
            df = pd.concat((df,objeto),ignore_index=True)
            time.sleep(0.1)
    print()
    print(df.shape[0]," trabajos agregados")
    return df

def BUscrap(limit=""):
    limit=int(limit)
    print("Capturando nuevos trabajos de www.bumeran.com.pe...")
    #options=webdriver.FirefoxOptions()
    options=Options()
    #username = 'spweyay4hc'
    #password = 'ur2xtC8aIhrb78nsQO'
    #proxy_server_url = f"http://{username}:{password}@pe.smartproxy.com:40000"
    #options=Options()
    service = Service(executable_path='./drivers/chromedriver')
    options.add_argument('--headless')
    #options.add_argument('--allow-host scrapbot.chambeala.com')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument(f'--proxy-server={proxy_server_url}')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
    #driver=webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    base_url="https://www.bumeran.com.pe/sitemap_avisos_bum.xml"
    HEADERS = {'Host': 'www.bumeran.com.pe',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-PE,en-US;q=0.8,de-DE;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.bumeran.com.pe/empleos.html',
                'Connection': 'keep-alive',
                'Cookie': '__cf_bm=2gUHwyBXpVgO7jHk1wycCD2Q8hBTsUxyyGOrwXPXUEw-1688582966-0-AZBjechbF1w42luFZunTWYDfzWZIBckZx2E+5Ls6lVLQKLwhBnCk5ZlgfYH2eCmH90EuHZe/d/W3/L/kUfymKJw=; frpo-cki="76d722b048786c45"',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Sec-GPC': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
    }
    r = requests.get(base_url,headers=HEADERS)
    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'xml')
    s= soup.find_all('loc')
    t= soup.find_all('lastmod')
    jobs=[]
    depas=[]
    distritos=[]
    dates=[]
    cat=[]
    #colisiones=[]
    desc=[]
    hipervinculos=[]
    newFound=0
    #for i in range(len(s)):
    for i in range(limit):
        pfecha=t[i].text.split('-')
        dates.append(date(int(pfecha[0]),int(pfecha[1]),int(pfecha[2])))
        driver.get(s[i].text)
        #print(i," ",s[i])
        titulo=driver.find_element('xpath','//h1')
        #titulo=driver.find_element(By.CLASS_NAME, "sc-kZUnxY")
        titulo=titulo.text.split("\n")[0]
        contenido=driver.find_element('xpath','//div[@id="section-detalle"]')
        ubicacion=driver.find_elements('xpath','//div[@id="section-detalle"]//h2')[1]
        ubicacion=ubicacion.text
        contenido=contenido.get_attribute('innerHTML')
        descript=contenido[contenido.find("<p>"):]
        descript=descript[:descript.find('<div class="sc-bFNFop gaCxJs">')]
        ubi=ubicacion.split(",")
        if len(ubi)>2:
            depas.append(ubi[1])
        else:
            depas.append(ubi[0])
        distritos.append(ubi[0])
        jobs.append(titulo)
        #descript='\n'.join(cont_list[2:])
        desc.append(descript)
        cat.append(categoriaB(descript))
        hipervinculos.append(s[i].text)
        newFound+=1
        sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
        #print("\r"+"*"*newFound+str(int(newFound/limit*100))+"%")
        sys.stdout.flush()
    print()
    print(newFound," nuevos trabajos descubiertos")
    driver.quit()
    print("Iniciando procesamiento...")
    ###dump in pandas
    df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
        "department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
        "validated","adtype_id","created_at"])
    for i in range(len(jobs)):
        #print(depas[i]," ",distritos[i])
        ubigeo=get_ubigeo(depas[i].strip(),distritos[i])
        if len(ubigeo)>=3:    
            hasheo=get_random_string(7)
            slug=slugify(desc[i])
            #print(i,"--->")
            objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
                    'description':desc[i],'url':hipervinculos[i],'slug':slug+'-'+hasheo,'category_id':cat[i],
                    'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':dates[i],
                    'date_to':dates[i]+timedelta(days=30),'imported':0,'date_created':dates[i],'status':1,'validated':1,
                    'adtype_id':1,'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            objeto = pd.DataFrame([objeto])
            df = pd.concat((df,objeto),ignore_index=True)
            time.sleep(0.1)
            print("*",end="")
    print()
    print(df.shape[0]," trabajos agregados")
    return df

def catMap(titulo):
    #2 Administracion,3 Aduana,4 Transporte,10 Contabilidad,17 Ingenieria, 19 Legales,37 prácticas,44 economia, 48 Técnico, 58 Auditoria, 87 Operaciones, 61 Agricultura
    catmap={'practicante':37,'abogado':19,'innova':17,'calidad':2,'limpieza':30,
    'ingenie':17,'admin':2,'derecho':19,'aduanas':3,
    'notificador':87,'abogados':19,'registrador':87,'orientador':87,
    'tributaria':10,'legal':19,'cuentas':10,'fiscal':2,
    'coordinador':2,'auditor':58,'técnico':48,
    'chofer':4,'presupuesto':44,'guardaparque':61,'justicia':19}
    for key in catmap:
        if key in titulo.lower():
            return catmap[key]
    return 51

def AQPscrap():
    base_url='https://www.convocatoriasdetrabajo.com/buscar-trabajos-en-AREQUIPA-4.html'
    HEADERS = {'User-Agent' :'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    r = requests.get(base_url,headers=HEADERS)
    print("Capturando nuevos trabajos de www.convocatoriasdetrabajo.com...")
    soup = BeautifulSoup(r.content, 'html.parser')
    s= soup.find_all('section',class_='conv-header')
    t= soup.find_all('div',class_='conv-detalle')
    only_fans=SoupStrainer(["h2","div","p","ul"])
    endpoints=[]
    jobs=[]
    desc=[]
    dates=[]
    cats=[]
    newFound=0
    limit=len(s)*2
    for i,tags in enumerate(s):
        endpoints.append(tags.find('a',href=True).get('href'))
        jobs.append(tags.text)
        dates.append(t[i].find('span').text.split()[-1])
        cats.append(catMap(tags.text))
        newFound+=1
        sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
        sys.stdout.flush()
    for ep in endpoints:
        codHTML=[]
        r=requests.get('https://www.convocatoriasdetrabajo.com/'+ep)
        soup = BeautifulSoup(r.content, 'html.parser',parse_only=only_fans)
        req=soup.find_all('h2')[1] #Requisitos
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling.next_sibling.next_sibling #Condiciones
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling.next_sibling.next_sibling #Como postular
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling.next_sibling.next_sibling #Recomendaciones
        codHTML.append(req.encode_contents())
        req=req.next_sibling.next_sibling
        codHTML.append(req.encode_contents())
        desc.append(b''.join(codHTML))
        newFound+=1
        sys.stdout.write("\r"+"*"*newFound+" "+str(int(newFound/limit*100))+"%")
        sys.stdout.flush()
    print()
    print(newFound//2," nuevos trabajos descubiertos")
    print("Iniciando procesamiento...")
    ###dump in pandas
    df = pd.DataFrame(columns=["hash","title","clicks","user_id","description","slug","category_id",
        "department_id","province_id","district_id","date_from","date_to","imported","date_created","status",
        "validated","adtype_id","created_at"])
    limit=limit//2
    for i in range(len(jobs)):
        ubigeo=[4,401,40101]
        hasheo=get_random_string(7)
        desc[i]=desc[i].decode('utf-8')
        slug=slugify(jobs[i]+desc[i])
        dates[i]=datetime.strptime(dates[i],"%d/%m/%Y")
        objeto ={'hash':hasheo,'title':jobs[i],'clicks':0,'user_id':random.randint(3,15),
                'description':desc[i],'url':'https://www.convocatoriasdetrabajo.com/'+endpoints[i],'slug':slug+'-'+hasheo,'category_id':cats[i],
                'department_id':ubigeo[0],'province_id':ubigeo[1],'district_id':ubigeo[2],'date_from':dates[i]-timedelta(days=30),
                'date_to':dates[i],'imported':0,'date_created':dates[i]-timedelta(days=30),'status':1,'validated':1,
                'adtype_id':1,'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        objeto = pd.DataFrame([objeto])
        df = pd.concat((df,objeto),ignore_index=True)
        sys.stdout.write("\r"+"*"*(i+1)+" "+str(int((i+1)/limit*100))+"%")
        sys.stdout.flush()
    print()
    print(df.shape[0]," trabajos agregados")
    return df

def dumpSqLite(df):
    con = sqlite3.connect("db.sqlite3")
    df.to_sql('myapp_trabajos', con, if_exists="replace",index=True,index_label='id')
    con.close()
    print()
    print("Listo.")

def dump(df,baseDatos):
    if baseDatos=="0":
        return
    try:
        with connect(
            host="162.55.232.15",
            user="chambeala_staging",
            #user="root",
            password="chambeala@2022!staging",
            #password="",
            database= "chambeal_staging" if baseDatos=="1" else "chambeal_db",
            #database="trabajos",
        ) as connection:
            db_data = "mysql+pymysql://"+ connection.user+":"+ parse.quote(connection._password) +"@162.55.232.15/"+connection.database+"?charset=utf8mb4"
            #print(db_data)
            engine = create_engine(db_data)
            #df.to_sql('myapp_trabajos',engine,if_exists='replace',index=True,index_label='id')
            df.to_sql('ads',engine,if_exists='append',index=False)
            engine.dispose()
            print()
            print("Listo.")

    except Error as e:
        print(e)
        
tl=Timeloop()

@tl.job(interval=timedelta(seconds=20))
def timedScrap():
    df=scrap(1)
    #dump(df)
    dumpSqLite(df)

if __name__ == "__main__":
    if len(sys.argv)>2:
        if sys.argv[1]=="1":
            df=CTscrap(sys.argv[2])
            dump(df,sys.argv[3])
        elif sys.argv[1]=="2":
            df=AQPscrap()
            dump(df,sys.argv[2])
        elif sys.argv[1]=="3":
            df=BUscrap(sys.argv[2])
            dump(df,sys.argv[3])
        elif  sys.argv[1]=="4":
            df=TRDscrap(sys.argv[2])
            dump(df,sys.argv[3])    
    else:
        print("Faltan argumentos.")
'''
df=BUscrap(sys.argv[1])

df=AQPScrap()
dump(df,"1")
'''
