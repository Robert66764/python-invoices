#Importing the necessary Python linraries
import re
import requests
import pdfplumber
import pandas as pd
from collections import namedtuple
import datetime

#A variable with the pdf report. 
ap = 'apreports.pdf'

#Obtaining the 16th page of the pdf document. 
with pdfplumber.open(ap) as pdf:
    page = pdf.pages[16]
    text = page.extract_text()

#Utilizing regex to extract data.
new_vend_re = re.compile(r'^\d{3} [A-Z].*')

#A tuple containing all the necessary fields. 
Inv = namedtuple('Inv', 'vend_num vend_name inv_dt due_dt inv_amt net_amt description')

#Data transformation. 
for line in text.split('\n'):
    if new_vend_re.match(line):
        vend_num, *vend_name = line.split()
        vend_name = ' '.join(vend_name)

#Utilizing regex in the invoices. 
inv_line_re = re.compile(r'(\d{6}) (\d{6}) ([\d,]+\.\d{2}) [\sP]*([\d,]+\.\d{2}) [YN ]*\d (.*?) [*\s\d]')

#Perfroimg an append with the various line times of the invoice. 
line_items = []
for line in text.split('\n'):
    if new_vend_re.match(line):
        vend_num, *vend_name = line.split()
        vend_name = ' '.join(vend_name)    
    
    line = inv_line_re.search(line)
    if line:
        inv_dt = line.group(1)
        due_dt = line.group(2)
        inv_amt = line.group(3)
        net_amt = line.group(4)
        desc = line.group(5)
        line_items.append(Inv(vend_num, vend_name, inv_dt, due_dt, inv_amt, net_amt, desc))

df = pd.DataFrame(line_items)


df['inv_amt'] = df['inv_amt'].map(lambda x: float(x.replace(',', '')))
df['net_amt'] = df['net_amt'].map(lambda x: float(x.replace(',', '')))

#Transforming string data to dates. 
for line in text.split('\n'):
    line = inv_line_re.search(line)
    if line:
        inv_dt = line.group(1)
        due_dt = line.group(2)
        format = '%m%d%y'
        datetime_str_inv = datetime.datetime.strptime(inv_dt, format)
        datetime_str_due = datetime.datetime.strptime(due_dt, format)

#Converting the invoice and due date columns from string to date. 
df['inv_dt'] = datetime_str_inv
df['due_dt'] = datetime_str_due

#Writing to a csv file called invoices.csv
df.to_csv('invoices.csv')



