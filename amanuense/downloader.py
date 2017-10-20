import asyncio
import io
import re
import sys

import aiohttp
from PyPDF2 import PdfFileMerger
import requests
from tqdm import tqdm

from exceptions import DiarioNotFoundOnDate

__all__ = 'download_DOU'


def diario_URL(secao, date):
    ''' Returns an URL for a Diário published on the given date '''
    URL = ('http://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp'
           '?jornal={0}&pagina=1&data={1}'.format(secao, date))
    return URL


def request_diario_info(section, date):
    ''' Request the Diário URL and returns the response '''
    URL = diario_URL(section, date)
    diario_info = requests.get(URL)
    diario_info.raise_for_status()
    return diario_info


def diario_not_found(diario_info):
    NOT_FOUND = ('Não foi encontrado nenhuma arquivo para os parâmetros '
                 'informados. Verifique a data e a página.')

    if NOT_FOUND in diario_info.text:
        return True
    else:
        return False


def diario_page_count(diario_info):
    ''' Extract the page count from the diario info '''
    PATTERN = 'Arquivos=\d{1,3}(?=")'
    match = re.search(PATTERN, diario_info.text, flags=re.DOTALL).group()
    page_count = int(match.split('=')[1])
    return page_count


def create_page_URL(secao, page_number, date):
    ''' Creates an URL pointing to a PDF page from a given section and
        date of Diário Oficial da União '''

    URL = ('http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?'
           'jornal={0}&pagina={1}&data={2}&captchafield='
           'firistAccess'.format(secao, page_number, date))
    return URL


def chunks(l, size):
    ''' Yield successive n-sized chunks from l. '''
    for i in range(0, len(l), size):
        yield l[i:i + size]


async def download_chunks(loop, URLs, pbar):
    ''' Download diario pages from a list of URLs '''
    async with aiohttp.ClientSession(loop=loop) as client:
        to_do = [download_PDF(client, URL, pbar) for URL in URLs]
        responses = await asyncio.gather(*to_do)
    return responses


async def download_PDF(client, URL, pbar):
    ''' Download a diario page and return its contents '''
    async with client.get(URL) as response:
        assert response.status == 200
        pbar.update(1)
        return await response.read()


def write_pages_to_PDF(pages, filepath):
    ''' Write Diário pages in a list to a pdf file on the disk '''
    pdf = PdfFileMerger()

    for page in pages:
        fileobj = io.BytesIO(page)
        pdf.append(fileobj=fileobj)

    pdf.write(filepath)
    pdf.close()


def jornal_URLs(section, date):
    ''' Returns a list with URLs to the Diário pages '''
    diario_info = request_diario_info(section, date)
    if diario_not_found(diario_info):
        raise DiarioNotFoundOnDate(date)

    page_count = diario_page_count(diario_info)
    URLs = [create_page_URL(section, n, date)
            for n in range(1, page_count + 1)]
    return URLs


def download_pages(URLs):
    '''' Asynchronously downloads a list of URLs refering to Diário pages'''
    loop = asyncio.get_event_loop()
    pages = []
    with tqdm(total=len(URLs)) as pbar:
        for chunk in chunks(URLs, size=10):
            res = loop.run_until_complete(download_chunks(loop, chunk, pbar))
            pages.extend(res)
    loop.close()
    return pages


def download_diario(section, date, filepath):
    ''' Download the content of a Diário on a given date to a file '''
    URLs = jornal_URLs(section, date)
    pages = download_pages(URLs)

    print('Writing pages to pdf {0}...'.format(filepath))
    write_pages_to_PDF(pages, filepath=filepath)
    print('Done.')


if __name__ == '__main__':
    secao = sys.argv[1]
    date = sys.argv[2]
    output = sys.argv[3]
    download_diario(secao, date, output)
