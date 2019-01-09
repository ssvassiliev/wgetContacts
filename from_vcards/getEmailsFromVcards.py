#!/usr/bin/python
import requests
import vobject
from bs4 import BeautifulSoup
import sys
from progress.bar import Bar
import io
# Installation:
# sudo pip install beautifulsoup4 requests progress vobject


def get_html_page(url):
    try:
        vc = requests.get(url, timeout=5).content
    except requests.exceptions.ConnectTimeout:
        try:
            vc = requests.get(url, timeout=10).content
        except requests.exceptions.ConnectTimeout:
            try:
                vc = requests.get(url, timeout=10).content
            except requests.exceptions.ConnectTimeout:
                print "Connection failed!\n"
                exit()
    return(vc)


def get_contact_from_vcard(url):
    vcard = vobject.readOne(vc)
    given = vcard.contents['n'][0].value.given
    family = vcard.contents['n'][0].value.family
    title = []
    if vc.find("EMAIL") != -1:
        email = vcard.contents['email'][0].value
    else:
        email = ""
    if vc.find("TITLE") != -1:
        for ti in vcard.contents['title']:
            title.append(ti.value)
    line = given + ';' + family + ';' + email + ';' + ','.join(title)
    line = line.decode('utf-8') + '\n'
    return(line)


dept_field = 6
head = u"firstname; lastname; email; title\n"
f1 = open(sys.argv[1], "r")
for url in f1:
    url = url.replace("\n", "")
    department = url.split("/")[dept_field]
    print '\nRetrieving ' + department + ' phonebook'
    page = requests.get(url).content
    filename = department + '_emails.csv'
    f2 = io.open(filename, 'w', encoding='utf-8')
    f2.write(head)
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.find_all("table")
    skip = 0
    bl = 0
    el = 0
    for each_table in tables:
        tr = each_table.find_all('tr')
        td = tr[0].find_all('td')
        if len(td) < 3:
            skip += 1
            continue
        bar = Bar('Loading', max=len(tr))
        for each_tr in tr:
            td = each_tr.find_all('td')
            bar.next()
            if str(td[2]).find("phonebook") == -1:
                continue
            url = td[2].a['href'].encode("utf-8").replace("?dn", "?vcard")
            vc = get_html_page(url)
            if vc.find("VCARD") != -1:
                line = get_contact_from_vcard(url)
                if line.split(';')[2] == '':
                    el = el + 1
                if line.split(';')[3] == '\n':
                    line = line.strip('\n') + td[1].text.strip('\n') + "\n"
            else:
                bl = bl + 1
                spl = td[0].text.split(" ")
                given = spl[0]
                spl.pop(0)
                family = ''
                for i in spl:
                    family = family + i
                line = given + ";" + family + ";;" + td[1].text.strip('\n')
                line = line + "\n"
            f2.write(line)
        bar.finish()
    f2.close()
    if skip != 0:
        ln = "** Warning: skipped " + str(skip) + " table"
        if skip != 1:
            ln = ln + "s"
        print ln
    if bl != 0:
        print "** Warning: " + str(bl) + " broken hyperlink(s) to vcards"
    if el != 0:
        print "** Warning: " + str(el) + " emails missing in vcards"
f1.close()
