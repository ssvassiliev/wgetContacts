#!/usr/bin/python
import requests
import vobject
from bs4 import BeautifulSoup
import sys
from progress.bar import Bar
import io
import re
# Installation:
# sudo pip install beautifulsoup4 requests progress vobject

dept_field = 4
url_col = 0

head = u"firstname; lastname; email; title\n"
f1 = open(sys.argv[1], "r")
for url in f1:
    url = url.replace("\n", "")
    department = url.split("/")[dept_field]
    if url.find("fredericton") != -1:
        department = department + "-fredericton"
    else:
        department = department + "-saintjohn"
    print "extracting contacts from department of " + department
    page = requests.get(url).content
    filename = department + '_emails.csv'
    f2 = io.open(filename, 'w', encoding='utf-8')
    f2.write(head)
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.find_all("table")
    skip = 0
    bl = 0
    for each_table in tables:
        tr = each_table.find_all('tr')
        tr.pop(0)
        td = tr[0].find_all('td')
        if len(td) < 2:
            skip += 1
            continue
        bar = Bar('Loading', max=len(tr))
        for each_tr in tr:
            td = each_tr.find_all('td')
            bar.next()
            if str(td[url_col]).find("href") == -1:
                continue
            if str(td[url_col]).find("phonebook") != -1:
                print " Skipping Unexpected reference to phonebook!"
                continue
            phBk = 'https:' + td[url_col].a['href'].encode("utf-8").strip('http:')
            try:
                vc = requests.get(phBk, timeout=5).content
            except requests.exceptions.ConnectTimeout:
                try:
                    vc = requests.get(phBk, timeout=10).content
                except requests.exceptions.ConnectTimeout:
                    try:
                        vc = requests.get(phBk, timeout=10).content
                    except requests.exceptions.ConnectTimeout:
                        print "Connection failed!\n"
                        exit()
            hotsoup = BeautifulSoup(vc, "html.parser")
            h1 = hotsoup.find_all('h1')
            if len(h1) < 2:
                print " Skipping broken page!"
                continue
            fn = h1[1].text.split(' ')
            if vc.find("@unb.ca") != -1:
                email = re.findall('\w+@\w+\.{1}\w+', vc)
                spl = td[0].text.split(" ")
                line = fn[0] + ";" + fn[1] + ";" + email[0] + ";" + td[1].text.strip('\n') + "\n"
            else:
                bl += 1
                continue
            f2.write(line)
        bar.finish()
    f2.close()
    ln = "** Warning: skipped " + str(skip) + " table"
    if skip != 0:
        ln = ln + "s"
        print ln
    if bl != 0:
        print "** Warning: " + str(bl) + " emails not found"
f1.close()
