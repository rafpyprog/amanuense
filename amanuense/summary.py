from collections import OrderedDict
import re


def clean_summary(summary):
    parsed = []
    for i in summary:
        item = i.replace('.', '').strip()
        parsed.append(item)
    return parsed


def summary_to_dict(summary):
    summary_dict = {}
    for i in summary:
        find_page = re.search('[0-9]', i)
        item_name = i[:find_page.start()].strip()
        item_page_number = int(i[find_page.start():].strip())
        summary_dict[item_name] = item_page_number

    summary = OrderedDict(sorted(summary_dict.items(), key=lambda t: t[1]))
    return summary


def get_summary_content(page):
    content = []
    for i in page.splitlines():
        summary_item = '\n*<text.*?>[A-Z][a-z].*\s?\.\s{1,2}[0-9]{1,3}</text>\n*'
        is_sumario = re.match(summary_item, i)
        if is_sumario:
            text = is_sumario.group(0)
            text = text.split('>', 1)[1].replace('</text>', '')
            content.append(text)
    return content


def make_summary(page1):
    content = get_summary_content(page1)
    summary = clean_summary(content)
    summary = summary_to_dict(summary)
    return summary
