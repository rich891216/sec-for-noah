import requests
from urllib.request import Request, urlopen
import brotli
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

# put in the urls you want
URLS = {"Berkshire Hathaway Inc": "https://13f.info/manager/0001067983-berkshire-hathaway-inc"}
session = requests.Session()
BASE_URL = "http://13f.info"
funds = {}

for fund, url in URLS.items():
    session.get(url)
    cookies = session.cookies.get_dict()
    userCookie = "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Cookie": userCookie,
    'Content-Type': 'application/javascript',
    'Content-Encoding': 'br'
    }
    req = Request(url)
    for k, v in headers.items():
        req.add_header(k, v)
    page = urlopen(req)
    response_body = page.read()
    decoded = brotli.decompress(response_body)
    html = decoded.decode("utf-8")
    # print(html)
    
    # split the html string into rows in the table
    rows = html.split('<tr')
    # print(rows[2])
    # print("-------------------------")
    # rows[2] is the first row of data
    data = rows[2].split('<td')
    d = {}

    quarter_data = data[1]
    holdings_data = data[2]
    value_data = data[3]
    top_holdings_data = data[4]
    form_type_data = data[5]
    date_filed_data = data[6]
    filing_id_data = data[7]

    
    d["quarter"] = quarter_data[quarter_data.find('>', quarter_data.find('href'))+1:quarter_data.find('</a>')]
    d["holdings"] = holdings_data[holdings_data.find('>')+1:holdings_data.find('<')]
    d['value'] = value_data[value_data.find('>')+1:value_data.find('<')]
    d['top holdings'] = top_holdings_data[top_holdings_data.find('title="')+len('title="'):top_holdings_data.find('">')]
    d["form type"] = form_type_data[form_type_data.find('title="')+len('title="'):form_type_data.find('">')]
    d["date filed"] = date_filed_data[date_filed_data.find('>')+1:date_filed_data.find('</td>')]
    d["filing id"] = filing_id_data[filing_id_data.find('>')+1:filing_id_data.find('</td>')]
    
    
    funds[fund] = d


    reference_link_start = quarter_data.find('href="') + len('href="')
    reference_link_end = quarter_data.find('">', reference_link_start)
    reference_link = BASE_URL + quarter_data[reference_link_start:reference_link_end]

    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)

    htmlSource = driver.page_sorce
    print(htmlSource)



    # new session for next link
    session.close()
    session.get(reference_link)
    cookies = session.cookies.get_dict()
    userCookie = "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Cookie": userCookie,
    'Content-Type': 'application/javascript',
    'Content-Encoding': 'br'
    }
    quarter_request = Request(reference_link)
    
    
    for k, v in headers.items():
        quarter_request.add_header(k, v)


    quarter_page = urlopen(quarter_request)
    quarter_body = quarter_page.read()
    quarter_decoded = brotli.decompress(quarter_body)
    quarter_html = quarter_decoded.decode("utf-8")

    quarter_rows = quarter_html.split('<tr')

    # print(quarter_html)

    table = pd.read_html(quarter_html)
    print(table)




print(funds)