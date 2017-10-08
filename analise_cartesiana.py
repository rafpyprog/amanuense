#https://estruturaorganizacional.dados.gov.br/doc/orgao-entidade/completa.xml

import re
import math
from lxml import etree
from subprocess import Popen, PIPE
from itertools import compress

from sumario import *

def pos(element):
    x, y = int(element.attrib['x']), int(element.attrib['y'])
    return x, y


def get_top(element):
    return int(element.attrib['top'])


def get_left(element):
    return int(element.attrib['left'])


def index_dist(element):
    xa, ya = element
    xb, yb = 0, 0
    distance = math.sqrt((xb - -xa) ** 2 + (yb - -ya) ** 2)
    return distance



ABOVE, BELLOW = 10, 11
def relative_vertical_pos(a, b):
    xa, ya, = coord(a)
    xb, yb, = coord(b)
    if yb < ya:
        return BELLOW
    else:
        return ABOVE

LEFT, RIGHT = 20, 21
def relative_horizontal_pos(a, b):
    xa, ya, = coord(a)
    xb, yb, = coord(b)
    if xa < xb:
        return LEFT
    else:
        return RIGHT

def get_pages():
    p = Popen(['pdftohtml', '-xml', '-i', '-stdout','DOUS1.pdf'], stdout=PIPE)
    stdout, err = p.communicate()
    document = etree.fromstring(stdout)
    pages = document.getchildren()
    return pages

def get_first_element(page):
    elements.sort(key=lambda x: [coord(x)[1], coord(x)[0]])
    return elements[4]


def get_page(xml, page_number):
    pattern = f'(<page number="{page_number}").*?</page>'
    m = re.search(pattern, xml, flags=re.DOTALL)
    page_start, page_end = m.span()
    return xml[page_start:page_end]


def clean_up(page):
    #clean_fontspec = re.sub('\t*<fontspec.*/>\r*\n*', '', page)
    clean_o = re.sub('\t*<text.*<b>o-</b>.*/text>\r*\n', '', page)
    clean_ISSN = re.sub('\t*<text.*>(ISSN).*?</text>\r*\n', '', clean_o)
    clean_ano = re.sub('\t*<text.*>(Ano).*?(ICP-Brasil)\.</text>\r*\n', '', clean_ISSN, flags=re.DOTALL)
    clean_dot = re.sub('\t*<text.*>\.</text>\r*\n', '', clean_ano)
    clean_header = re.sub('<text.*>N.*?(ICP-Brasil)\..*?\d{1,3}</text>\r*\n*', '', clean_dot, flags=re.DOTALL)
    clean_exemplar = re.sub('\t*<text.*>EXEMPLAR DE ASSINANTE DA IMPRENSA NACIONAL</text>\r*\n', '', clean_header)
    clean_comercio = re.sub('\t*<text.*>COMERCIALIZAÇÃO PROIBIDA POR TERCEIROS</text>\r*\n', '', clean_exemplar)
    return clean_comercio


def parse_pages(xml, page_count):
    pages = [get_page(xml, page_number=i) for i in range(1, page_count + 1)]
    clean_pages = [clean_up(page) for page in pages]
    return clean_pages


def is_h1(element):
    if element is None:
        return False
    ORGAOS = ['Defensoria', 'Editais', 'Entidades', 'Ineditoriais',
              'Ministério', 'Poder', 'Presidência', 'Tribunal',
              'Conselho Nacional']
    regex = '^' + '|'.join(ORGAOS)
    element_text = element.xpath('string()')
    is_valid = re.match(regex, element_text) is not None

    font = element.attrib.get('font', False)
    if is_valid and font in ('4', '5'):
        return True
    return False


class Heading():
    def __init__(self, element, tag_name, regex, valid_sizes=[]):
        self.element = element
        self.tag_name = tag_name
        self.valid_sizes = valid_sizes
        self.regex = regex

    def tag(self):
        if self.is_valid is True:
            self.element.tag = self.tag_name
        else:
            msg = "Element is not a valid {} heading."
            raise ValueError(msg.format(self.tag_name))

    def merge_parts(self):
        next_element = self.element.getnext()
        if next_element is not None:
            if self.get_font_size(next_element) == self.font_size:
                text_part1 = self.element.xpath('string()')
                text_part2 = next_element.xpath('string()')
                self.element.text = ' '.join([text_part1, text_part2])

                parent = self.element.getparent()
                parent.remove(next_element)
                return True
        return False

    @property
    def text(self):
        return self.element.text

    @property
    def font_size(self):
        return self.get_font_size(self.element)

    def get_font_size(self, element):
        size = element.attrib.get('font', False)
        return int(size)

    @property
    def text(self):
        text = self.element.xpath('string()')
        return text

    @property
    def text_is_valid(self):
        text_is_valid = re.match(self.regex, self.text) is not None
        return text_is_valid

    @property
    def font_size_is_valid(self):
        return self.font_size in self.valid_sizes

    @property
    def is_valid(self):
        if self.font_size_is_valid and self.text_is_valid:
            return True
        else:
            return False


class H1(Heading):
    def __init__(self, element):
        TAG = 'h1'
        valid_sizes = (4, 5)
        self.validators = ['Defensoria', 'Editais', 'Entidades', 'GABINETE'
                           'Ineditoriais', 'Ministério', 'Poder',
                           'Presidência', 'Tribunal', 'Conselho Nacional']
        validator = '^' + '|'.join(self.validators)
        Heading.__init__(self, element, regex=validator, tag_name=TAG,
                         valid_sizes=valid_sizes)




def is_h2(element):
    font_size = element.attrib.get('font', False)
    if font_size in ('10', '11'):
        element_text = element.xpath('string()').strip()
        for ch in element_text:
            if ch.isalpha() and ch.isupper() is False:
                return False
        return True
    else:
        return False


def is_h3(element):
    font_size = element.attrib.get('font', False)
    match = re.match('^EXTRATO', element.xpath('string()'))
    if font_size == '12' and match is not None:
        return True
    return False


def is_subtitle(element):
    font_size = element.attrib.get('font', False)
    if not font_size:
        return False
    else:
        if is_h2(element) is True:
            return True
        if is_h3(element)is True:
            return True


def make_heading(paginas_XML, heading):
    # Faz o merge dos titulos quebrados em duas linhas
    for page in paginas_XML:
        for i in page.getiterator():
            head = heading(i)
            if head.is_valid:
                head.merge_parts()
                head.tag()


def coord(element):
    x, y = int(element.attrib['left']), int(element.attrib['top'])
    return x, y


def dist_elementos(a, b):
    xa, ya = coord(a)
    xb, yb = coord(b)
    distance = math.sqrt((xb - -xa) ** 2 + (yb - -ya) ** 2)
    return distance


def mesmo_orgao(titulo, subtitulo, max_x=250, max_y=100):
    xa, ya = coord(titulo)
    xb, yb = coord(subtitulo)
    if ya < yb:
        if abs(xa - xb) < 250 and abs(ya - yb) < 100:
            return True
    return False


##############################################################################
def import_PDF(n):
    PDF = f'DOUS{n}.pdf'

    p = Popen(['pdftohtml', '-xml', '-i', '-stdout', '-enc', 'Latin1', PDF],
              stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    xml = stdout.decode('latin1')

    # Conta as páginas do PDF
    p = Popen(['pdfinfo', PDF], stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    info = stdout.decode('utf-8').splitlines()
    PAGE_COUNT = [int(i.split(':')[-1].strip()) for i in info if i.startswith('Pages')][0]

    pages = parse_pages(xml, page_count=PAGE_COUNT)

    paginas_XML = [etree.fromstring(p) for p in pages]
    return paginas_XML
    
make_heading(paginas_XML, H1)
make_heading(paginas_XML, H2)


for page_number, pagina in enumerate(paginas_XML):
    h1_tags = pagina.findall('h1')
    h2_tags = pagina.findall('h2')
    if h1_tags:
        print([i.xpath('string()') for i in h1_tags])
        print([i.xpath('string()') for i in h2_tags])
        for titulo in h1_tags:
            is_sub = [mesmo_orgao(titulo, subtitulo) for subtitulo in h2_tags]

            if any(is_sub) is False:
                subtitulos = [i for i in pagina.getchildren() if is_subtitle(i)]
                is_sub = [mesmo_orgao(titulo, sub) for sub in subtitulos]
            sub_filho = (list(compress(h2_tags, is_sub)))

            print(titulo.xpath('string()'), ':', sub_filho[0].xpath('string()'))





class H2(Heading):
    def __init__(self, element):
        TAG = 'h2'
        valid_sizes = (4, 5, 10, 11)
        #https://estruturaorganizacional.dados.gov.br/doc/orgao-entidade/completa.xml
        self.validators = ['AGÊNCIA', 'CASA', 'DEPARTAMENTO', 'COMANDO',
                           'COMANDO-GERAL', 'CONSELHO', 'GABINETE', 'INSTITUTO',
                           'UNIVERSIDADE',
                           'S\s*E\s*C\s*R\s*E\s*T\s*A\s*R\s*I\s*A']

        self.validator = '^' + '|'.join(self.validators)
        Heading.__init__(self, element, regex=self.validator, tag_name=TAG,
                         valid_sizes=valid_sizes)



elements = paginas_XML[0].getchildren()
for i in elements[400:430]:
    print(i.xpath('text()'))

    text = i.xpath('string()')
    if 'GABINETE' in text:
        print(text)
    else:
        print(text)


H1 = ['^(Atos do Poder Judiciário)$',
      '^(Presidência da República)$',
      '^Ministério da Agricultura,.*']

pattern = '|'.join(H1)
pagina = paginas_XML[0]
itens = pagina.getchildren()




paginas_XML = import_PDF(2)
p = paginas_XML[0]

fonts_spec(p)
