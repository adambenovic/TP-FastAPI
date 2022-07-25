import requests
from bs4 import BeautifulSoup

# toto je hnoj sluzi len proof of concept

def get_names(ico):
    URL = f'https://www.orsr.sk/hladaj_ico.asp?ICO={ico}&SID=0'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    x = soup.find("div", {"class": "bmk"})
    x = x.find('a')['href']
    URL = f'https://www.orsr.sk/{x}'
    page = requests.get(URL)
    page = BeautifulSoup(page.content, "html.parser")

    def parse_name(listspan):
        name = ''
        for i in listspan:
            if "s. r. o." in i.text or "a. s." in i.text:
                break
            table = i.parent
            if table.name != 'td':
                table = table.parent
            for x in table.children:
                if x.name == 'span':
                    name = name + ' ' + x.text.strip()
                if x.name == 'a':
                    for s in x.children:
                        name = name + ' ' + s.text.strip()
                    break
                if x.name == 'br': break
            break
        name = name.strip()
        return name

    names = []

    kon = page.find_all('span')

    for spans in kon:
        if 'Štatutárny orgán:' in spans.text:
            stat_org = spans.parent.parent.children
            next(stat_org)
            next(stat_org)
            next(stat_org)
            konatelia = next(stat_org)
            konatelia = konatelia.children
            next(konatelia)
            for i in konatelia:
                span = i.find_all('span')
                names.append(parse_name(span))

    names = [x for x in names if x != '']
    return names
