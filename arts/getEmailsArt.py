#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import sys
# Installation:
# sudo pip install beautifulsoup4 requests

head = "firstname; lastname; email; title\n"
f1 = open(sys.argv[1], "r")
for url in f1:
    url = url.replace("\n", "")
    if url.find("fredericton/cs/") != -1:
        department = url.split("/")[4]
    else:
        department = url.split("/")[6]
    if url.find("fredericton") != -1:
        department = department + "-fredericton"
    else:
        department = department + "-saintjohn"
    print "extracting contacts from department of " + department
    page = requests.get(url).content
    filename = department + '_emails.csv'
    f2 = open(filename, 'w')
    f2.write(head)
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table")
    tr = table.find_all("tr")
    tr.pop(0)
    for each_tr in tr:
        td = each_tr.find_all('td')
        name = td[0].text.split(" ")
        given = name[0]
        family = name[len(name)-1]
        line = given + ';' + family + ';' + td[3].a['href'] + ';' + td[1].text + '\n'
        line = line.replace("mailto:", "")
        f2.write(line)
    f2.close()
f1.close()
