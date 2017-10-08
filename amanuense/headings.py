import re
from lxml import etree


def font_attr(fontspec, attr):
    pattern = '{}=".*?"'.format(attr)
    attr = re.search(pattern, fontspec)
    match = attr.group()
    attr_value = match.split('=')[1].replace('"', '')
    return attr_value


def get_font_styles(page1):
    '''
    Busca nos fontspec do documento os id's das fontes referentes aos títulos
    do documento. Retorna dicionário com o header e o respectivo id.
    '''
    H1_SIZE = "15"
    H2_SIZE = "12"

    fonts = {'h1': '', 'h2': '', 'h3': ''}

    specs = [i for i in page1.splitlines() if 'fontspec' in i]
    assert(len(specs) > 0)
    for spec in specs:
        size = font_attr(spec, attr='size')
        fontid = font_attr(spec, attr='id')

        if size == H1_SIZE:
            fonts['h1'] = fontid
        elif size == H2_SIZE:
            if fonts['h2'] == '':
                fonts['h2'] = fontid


    fonts['h3'] = str(int(fonts['h2']) + 1)

    return fonts


def get_titles_by_heading(document, heading):
    text_elements = document.xpath('//text')
    titles = [i for i in text_elements if i.attrib.get('font') == heading]
    return titles
