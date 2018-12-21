#!/usr/bin/python
import requests
import vobject
from bs4 import BeautifulSoup
import sys
from progress.bar import Bar
# Installation:
# sudo pip install beautifulsoup requests progress vobject

head = "firstname; lastname; email; title\n"
f1 = open(sys.argv[1], "r")
for url in f1:
    url = url.replace("\n", "")
    department = url.split("/")[6]
    print '\nRetrieving ' + department + ' phonebook'
    page = requests.get(url).content
    filename = department + '_emails.csv'
    f2 = open(filename, 'w')
    f2.write(head)
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.find_all("table")
    skip = 0
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
            phBk = td[2].a['href'].encode("utf-8").replace("?dn", "?vcard")
            vc = requests.get(phBk).content
            if vc.find("VCARD") != -1:
                vcard = vobject.readOne(vc)
                given = vcard.contents['n'][0].value.given
                family = vcard.contents['n'][0].value.family
                additional = vcard.contents['n'][0].value.additional
                email = ""
                title = []
                if vc.find("EMAIL") != -1:
                    email = vcard.contents['email'][0].value
                if vc.find("TITLE") != -1:
                    for ti in vcard.contents['title']:
                        title.append(ti.value)
                line = given + ';' + family + ';' + email + ';' + ','.join(title) + '\n'
            else:
                line = ";;\n"
            f2.write(line)
        bar.finish()
    f2.close()
    ln = "** skipped " + str(skip) + " table"
    if skip != 1:
        ln = ln + "s"
    print ln
f1.close()
