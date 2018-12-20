#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8'

f1 = open(sys.argv[1], "r")
for url in f1:
    url = url.replace("\n", "")
    department = url.split("/")[6]
    print "extracting contacts from department of " + department
    page = requests.get(url).content
    filename = department + '_emails.csv'
    f2 = open(filename, 'w')
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table")
    tr = table.find_all("tr")
    for each_tr in range(1, len(tr)):
        td = tr[each_tr].find_all('td')
        line = td[0].text + ';' + td[3].a['href'] + ';' + td[1].text + '\n'
        line.replace("mailto:", "")
        f2.write(line)
    f2.close()
f1.close()
