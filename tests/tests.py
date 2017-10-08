from collections import OrderedDict
import json
import os
import random
from unittest.mock import MagicMock

import pytest

from amanuense import *
from amanuense.summary import get_summary_content, make_summary
from amanuense.headings import get_font_styles, font_attr

def data_dir():
    cwd = os.getcwd()
    data = 'tests/data/'
    data_dir = os.path.join(cwd, data)
    return data_dir

def data_files():
    n_files = 3
    files = []
    for i in range(1, n_files + 1):
        files.append(os.path.join(data_dir(), 'DOUS{}.pdf'.format(i)))
    return files


@pytest.fixture(scope="module")
def dou_number():
    return random.randint(1, 3)


@pytest.fixture(scope='module')
def pages(dou_number):
    pages = 'dou{}.pages'.format(dou_number)
    fp = os.path.join(data_dir(), pages)
    return json.loads(open(fp).read())


@pytest.fixture(scope='module')
def diario(dou_number, pages):
    pdf = os.path.join(data_dir(), 'DOUS{}.pdf'.format(dou_number))
    diario = Diario(pdf)
    #diario.parse_pages = MagicMock(return_value=pages)
    return diario


def test_diario_init(diario):
    assert isinstance(diario, Diario)

@pytest.mark.parametrize('pdf', data_files())
def test_pages(pdf):
    diario = Diario(pdf)
    assert isinstance(diario.pages, list)
    assert diario.pages != []

@pytest.mark.parametrize('pdf', data_files())
def test_page_count_equals_pages(pdf):
    diario = Diario(pdf)
    assert diario.page_count == len(diario.pages)


def test_toxml_decode_and_returns_valid_string(diario):
    fp = os.path.join(data_dir(), 'DOUS1.pdf')
    string = diario.toxml(fp, 'Latin1', decode=True)
    assert string not in ('', None)


def test_toxml_decode_and_returns_string(diario):
    fp = os.path.join(data_dir(), 'DOUS1.pdf')
    assert isinstance(diario.toxml(fp, 'latin1', decode=True), str)


@pytest.mark.parametrize('pdf', data_files())
def test_remove_page_header(pdf):
    diario = Diario(pdf)
    for n, page in enumerate(diario.pages):
        assert page.find('ICP-Brasil.</text>') == -1
        assert page.find('>Este documento pode ser verificado') == -1


@pytest.mark.parametrize('pdf', data_files())
def test_summary_content_is_list(pdf):
    diario = Diario(pdf)
    page1 = diario.pages[0]
    isinstance(get_summary_content(page1), list)


@pytest.mark.parametrize('pdf, expected', zip(data_files(), [21, 29, 27]))
def test_summary_content_has_all_items(pdf, expected):
    diario = Diario(pdf)
    page1 = diario.pages[0]
    content = get_summary_content(page1)
    assert len(content) == expected


@pytest.mark.parametrize('pdf, expected', zip(data_files(), [21, 29, 27]))
def test_male_summary(pdf, expected):
    diario = Diario(pdf)
    page1 = diario.pages[0]
    summary = make_summary(page1)
    assert len(summary) == expected


ATOS = 'Atos do Poder Judiciário'
PR = 'Presidência da República'
@pytest.mark.parametrize('pdf, expected', zip(data_files(), [ATOS, PR, PR]))
def test_make_summary(pdf, expected):
    diario = Diario(pdf)
    summary = diario.summary
    assert list(summary.keys())[0] == expected


@pytest.mark.parametrize('pdf, expected', zip(data_files(), [ATOS, PR, PR]))
def test_font_attr(pdf, expected):
    diario = Diario(pdf)
    page1 = diario.pages[0]
    specs = [i for i in page1.splitlines() if 'fontspec' in i]
    size = font_attr(specs[0], 'size')
    assert isinstance(size, str)
    assert size != ''
    assert len(size) <= 2

    id = font_attr(specs[0], 'id')
    assert isinstance(id, str)
    assert id != ''
    assert len(id) <= 2


@pytest.mark.parametrize('pdf, expected', zip(data_files(),
    [('5', '10', '11'),
     ('4', '5', '6'),
     ('5', '10', '11')]))
def test_get_font_styles(pdf, expected):
    diario = Diario(pdf)
    page1 = diario.pages[0]
    styles = get_font_styles(page1)
    assert isinstance(styles, dict)
    assert tuple(styles.values()) == expected
