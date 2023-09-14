import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import requests
from bs4 import BeautifulSoup
import re
from joblib import dump, load
import urllib3
import string
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username = 'spweyay4hc'
password = 'ur2xtC8aIhrb78nsQO'
proxy = f"http://{username}:{password}@pe.smartproxy.com:40000"
headers = {
    'authority': 'pe.computrabajo.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.5',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'ut=C0403C940FB220F6E2D3E4BF00CFE60771D6A56F5A9E68A60F2604F9FC9D99F5793C0C1F5539C30D; cla=B1C069000945525361373E686DCF3405',
    'origin': 'https://pe.computrabajo.com',
    'referer': 'https://pe.computrabajo.com/empleos-en-lima',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

def descripcion(identificador):
  data = {
    'oi': identificador
  }
  ret=""
  MAX_RETRIES=3
  for _ in range(MAX_RETRIES):
    try:
      response = requests.get('https://oferta.computrabajo.com/offer/'+identificador+'/d?ipo=3&iapo=1', headers=headers, proxies = {
      'http': proxy,'https': proxy}, timeout=(30,60), verify=False)
      if response.status_code in [200, 404]:
        break
    except requests.exceptions.ConnectTimeout:
      pass
    except requests.exceptions.SSLError:
      pass
    except requests.exceptions.ProxyError:
      pass
    except requests.exceptions.ConnectionError:
      pass
    except requests.exceptions.ReadTimeout:
      pass
  if response is None or response.status_code != 200:
    print('Request has timed out')
    return ret
  soup = BeautifulSoup(response.content, 'html.parser')
  #f = open("text.tmp", "wb")
  try:
    s= soup.find_all('div',class_='fs16')[1]
    #f.write(s.encode_contents())
    ret=s.encode_contents()
  except:
    #f.write(" ")
    ret="No codification available"
  #f.close()
  return ret

def slugify(text):
  if isinstance(text, bytes):
    text=text.decode('utf-8')
  clean = re.compile(r'<.*?>')
  text = re.sub(clean,'',text)
  x = re.findall("(?:\w+(?:\W+|$)){0,9}", text)
  replacements = (("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),("ñ", "n"),("ü", "u"))
  x = [i for i in x if i]
  try:
    y=x[0]
    for (a,b) in replacements:
      y=y.replace(a,b)
    y=re.sub('[^\w\d]',"-",y)
    y=y.strip("-")
    y=re.sub("-+","-",y)
  except:
    y=""
  return y
  
def categoria(descripcion):
    clf=load('clasificador.joblib')
    resp=clf.predict([descripcion])
    return resp[0]

def categoriaB(descripcion):
    clf=load('clasificadorB.joblib')
    resp=clf.predict([descripcion])
    return resp[0]

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
