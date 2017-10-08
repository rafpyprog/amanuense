def get_headings_font(document):
    '''
    Busca nos fontspec do documento os id's das fontes referentes aos títulos
    do documento. Retorna dicionário com o header e o respectivo id.
    '''
    H1_SIZE = "15"
    H2_SIZE = "12"

    specs = document.xpath('//fontspec')

    h1_font = [i.attrib['id'] for i in specs if i.attrib['size'] == H1_SIZE][0]
    h2_font = [i.attrib['id'] for i in specs if i.attrib['size'] == H2_SIZE][0]
    h3_font = str(int(h2_font) + 1)  # UPPERCASE

    return {'h1': h1_font, 'h2': h2_font, 'h3': h3_font}


def get_titles_by_heading(document, heading):
    text_elements = document.xpath('//text')
    titles = [i for i in text_elements if i.attrib.get('font') == heading]
    return titles
