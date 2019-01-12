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

# science
#dept_field = 6
#phonebk_col = 2
#ncol = 3

# renaissance
dept_field = 4
phonebk_col = 0
ncol = 2


def make_line_from_table(td, email):
    spl = td[0].text.split(" ")
    given = spl[0]
    spl.pop(0)
    family = ''
    for i in spl:
        family = family + ' ' + i
        line = given + ";" + family.strip() + ";" + email + ";" + td[1].text.strip('\n')
        line = line + "\n"
    return(line)


def get_phbk_url_from_page(html):
    url = ''
    lines = html.split('\n')
    for l in lines:
        if l.find("phonebook") != -1:
            url = (BeautifulSoup(l, "lxml").a['href'])
            break
    return(url)


def get_vcard_url_from_page(html):
    lines = html.split('\n')
    for l in lines:
        if l.find('?vcard') != -1 or l.find('?help=vcard') != -1:
            sp = BeautifulSoup(l, 'lxml')
            url = 'https://phonebook.unb.ca' + sp.a['href'].lstrip('.')
            break
    return(url)


def get_email_from_page(html):
    email = ''
    lines = html.split('\n')
    for l in lines:
        if l.find("mailto") != -1:
            email = BeautifulSoup(l, "lxml").a['href']
            email = re.sub("mailto:%20", "", email)
            break
    return(email)


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
    line = line.strip("\n")
    line = line.decode('utf-8') + '\n'
    return(line)


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
        if len(td) < ncol:
            skip += 1
            continue
        bar = Bar('Loading', max=len(tr))
        for each_tr in tr:
            td = each_tr.find_all('td')
            bar.next()
            if len(td) < ncol:
                print "\n** Error: The number of columns in the table changed"
                break
            u1 = td[phonebk_col].a['href'].encode("utf-8")
            if str(td[phonebk_col]).find("phonebook") == -1:
                u2 = re.sub('index.html', u1, url)
                page = get_html_page(u2)
                if page.find('phonebook') != -1:
                    u1 = get_phbk_url_from_page(page)
                elif page.find('mailto') != -1:
                    e1 = get_email_from_page(page)
                    line = make_line_from_table(td, e1)
                    f2.write(line)
                    continue
                else:
                    continue
            page = get_html_page(u1)
            u3 = get_vcard_url_from_page(page)
            vc = get_html_page(u3)
            if vc.find("BEGIN:VCARD") != -1:
                line = get_contact_from_vcard(u3)
                if line.split(';')[2] == '':
                    el = el + 1
                if line.split(';')[3] == '\n':
                    line = line.strip('\n') + td[1].text.strip('\n') + "\n"
            else:
                bl = bl + 1
                make_line_from_table(td, '')
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
        print "** Warning: " + str(el) + " email(s) missing in vcards"
f1.close()
