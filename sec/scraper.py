import requests
from urllib.request import Request, urlopen
import brotli
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import io

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

    # build reference link
    reference_link_start = quarter_data.find('href="') + len('href="')
    reference_link_end = quarter_data.find('">', reference_link_start)
    reference_link = BASE_URL + quarter_data[reference_link_start:reference_link_end]

    # open chrome (you can use firefox or other browsers, just look up selenium.webdriver)
    chrome_options = webdriver.ChromeOptions()
    download_dir = "~/Desktop/sec-for-noah/csv_files/"
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory':download_dir
    })

    # chrome_options.add_argument('download.default_directory=~/Desktop/sec-for-noah/csv_files')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(reference_link)

    # wait for results
    wait = WebDriverWait(driver, 10)
    results = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "tbody")))
    htmlSource = driver.page_source

    driver.find_element(By.XPATH, '//button[contains(span, "Download CSV")]').click()

    WebDriverWait(driver, 60)
    driver.close()

    # table = pd.read_html(io.StringIO(htmlSource))
    # print(table)
    file_name = fund + " " + d['quarter'] +" 13F Top Portfolio Holdings.csv"

    table = pd.read_csv('~/Desktop/sec-for-noah/csv_files/'+file_name)

print(funds)