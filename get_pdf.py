from subprocess import Popen, PIPE
import datetime
import random
import re
import os

from bs4 import BeautifulSoup
import requests

def get_PDF_URL(section, date):
    session = requests.Session()
    r = session.get('http://portal.imprensanacional.gov.br/')
    r.raise_for_status()


    payload = {"edicao.jornal_hidden": "", "edicao.paginaAtual": "1", "edicao.tipoPesquisa": "leitura_jornais", "edicao.jornal": str(section), "edicao.dtInicio": date[:5],
               "edicao.dtFim": date[:5], "edicao.ano": date[-4:]}



    consulta_URL = 'http://pesquisa.in.gov.br/imprensa/core/consulta2.action'

    response = session.post(consulta_URL, data=payload)
    print(response.url)
    soup = BeautifulSoup(response.text, 'html.parser')
    if 'Nenhum registro encontrado para a pesquisa.' in soup.text:
        print('nenhum')
        return False

    onclick_attr = soup.findAll('a')[-1]['onclick']
    URL = re.search('http.*[0-9]', onclick_attr)
    PDF_URL = onclick_attr[URL.start(): URL.end()]
    return PDF_URL




base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, 1800, 181)]

for dt in date_list:
    dt = dt.strftime('%d/%m/%Y')
    print(dt)
    secao = random.randrange(1, 4)
    url = get_PDF_URL(secao, dt)
    if url:
        PDF = requests.get(url)
        date_name = dt.replace('/', '')
        with open(f'DOU_{secao}_{date_name}.pdf', 'wb') as f:
            f.write(PDF.content)



url = get_PDF_URL(1, '07/10/2002')

pdfs = list(filter(lambda x: x.startswith('DOU_'), os.listdir()))

for fp in pdfs:
    p = Popen(['pdftohtml', '-xml', '-i', '-enc', 'UTF-8', fp], stderr=PIPE)
    out, err = p.communicate()



xmls = list(filter(lambda x: x.endswith('.xml'), os.listdir()))
print(len(xmls))
r = []
for fp in xmls:
    with open(fp, 'r', encoding='latin1') as f:
        content = f.read()
    #m = list(re.finditer('.*<text.*>\.*\s*[0-9]+</text>\r*\n*$', content))
    m = list(re.finditer('\s?\.+?\s{1,2}[0-9]+?<', content))
    print(len(m))
    CASA = list(filter(lambda x: '>CASA CIVIL<' in x, content.splitlines()))
    for i in CASA:
        r.append(i)
        print(i)

content[:4000].splitlines()
