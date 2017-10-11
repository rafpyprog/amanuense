from PyPDF2 import PdfFileMerger
import asyncio
import io
import re

import aiohttp
import requests


__all__ = ['download_DOU']


def journal_URL(journal, date):
    ''' Returns an URL for a journal published on the given date '''
    URL = (f'http://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp'
           f'?jornal={journal}&pagina=1&data={date}')
    return URL


def request_journal_info(journal, date):
    ''' Request the journal URL and returns the response '''
    URL = journal_URL(journal, date)
    journal_info = requests.get(URL)
    journal_info.raise_for_status()
    return journal_info


def journal_page_count(journal_info):
    ''' Extract the page count from the journal info '''
    PATTERN = 'Arquivos=\d{1,3}(?=")'
    match = re.search(PATTERN, journal_info.text, flags=re.DOTALL).group()
    page_count = int(match.split('=')[1])
    return page_count


def create_page_URL(section, page_number, date):
    ''' Creates an URL pointing to a PDF page from a given section and
        date of Diário Oficial da União '''

    URL = (f'http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?'
           f'jornal={section}&pagina={page_number}&data={date}&captchafield='
           'firistAccess')
    return URL


def chunks(l, size):
    ''' Yield successive n-sized chunks from l. '''
    for i in range(0, len(l), size):
        yield l[i:i + size]


async def download_chunks(loop, URLs):
    ''' Download journal pages from a list of URLs '''
    async with aiohttp.ClientSession(loop=loop) as client:
        to_do = [download_PDF(client, URL) for URL in URLs]
        responses = await asyncio.gather(*to_do)
    return responses


async def download_PDF(client, URL):
    ''' Download a journal page and return its contents '''
    async with client.get(URL) as response:
        assert response.status == 200
        return await response.read()


def write_pages_to_PDF(pages, filepath):
    ''' Write journal pages in a list to a pdf file on the disk '''
    pdf = PdfFileMerger()

    for page in pages:
        fileobj = io.BytesIO(page)
        pdf.append(fileobj=fileobj)

    pdf.write(filepath)
    pdf.close()


def jornal_URLs(section, date):
    ''' Returns a list with URLs to the journal pages '''
    data = request_journal_info(section, date)
    page_count = journal_page_count(data)
    URLs = [create_page_URL(section, n, date) for n in range(1, page_count + 1)]
    return URLs


def download_pages(URLs):
    '''' Asynchronously downloads a list of URLs refering to journal pages'''
    loop = asyncio.get_event_loop()
    pages = []
    for n, chunk in enumerate(chunks(URLs, size=20)):
        print(n)
        res = loop.run_until_complete(download_chunks(loop, chunk))  # <12>
        pages.extend(res)
    loop.close()
    return pages


def download_diario(section, date, filepath):
    ''' Download the content of a journal on a given date to a file '''
    URLs = jornal_URLs(section, date)
    pages = download_pages(URLs)
    write_pages_to_PDF(pages, filepath=filepath)
