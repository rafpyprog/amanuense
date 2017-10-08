import urllib3
from lxml import etree
import requests
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_SIORG():
    url_siorg = ('https://estruturaorganizacional.dados.gov.br/doc/orgao-'
                 'entidade/completa.xml')
    r = requests.get(url_siorg, verify=False)
    xml = r.content
    SIORG = etree.fromstring(xml)
    return SIORG

SIORG = get_SIORG()

FEDERAL = 'https://estruturaorganizacional.dados.gov.br/id/esfera/1'
ESTADUAL = 'https://estruturaorganizacional.dados.gov.br/id/esfera/2'

#codigoPoder
EXECUTIVO = 'https://estruturaorganizacional.dados.gov.br/id/poder/1'
LEGISLATIVO = 'https://estruturaorganizacional.dados.gov.br/id/poder/2'
JUDICIARIO = 'https://estruturaorganizacional.dados.gov.br/id/poder/3'



def unidade_pai(unidade):
    cod_pai = unidade.find('codigoUnidadePai').xpath('text()')[0]
    r = requests.get(cod_pai, verify=False, )
    dados = json.loads(r.content)
    return dados['unidade']['nome']

for i in SIORG.xpath(f'./unidades[codigoPoder[text()="{EXECUTIVO}"]]'):
    print(unidade_pai(i))

    print(i.find('nome').xpath('text()'))



def estrutura_organizacional(unidade):
    url = f'http://estruturaorganizacional.dados.gov.br/doc/unidade-organizacional/{unidade}/estrutura'
    r = requests.get(url)
    dados = json.loads(r.content)
    return dados['estrutura']

e = estrutura_organizacional(26)
e['estrutura']
