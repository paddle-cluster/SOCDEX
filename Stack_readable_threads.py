#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##MAKE PDF VERSIONS OF THREADS

from urllib.request import urlopen
from bs4 import BeautifulSoup
from weasyprint import HTML
import re
import csv

with open('selected_ids.csv') as input:
    reader = csv.reader(input)
    id_list = list(reader)

def main(id_list):
    if len(id_list) > 0:
        url = "http://www.stackprinter.com/export?format=HTML&service=stackoverflow&printer=false&question={}".format(id_list[0])


        bs = BeautifulSoup(urlopen(url), 'lxml')
        title = bs.title.string.replace('/', ' or ')

        print("\n" + title + "\n" + url)

        HTML(url).write_pdf("{}.pdf".format(title))
        return main(id_list[1:])

    print("\nPrinted all the pages...")

if __name__ == '__main__':
    main(id_list)

