import requests
from urllib.request import Request, urlopen
import brotli

# put in the urls you want
URLS = {"Berkshire Hathaway Inc": "https://13f.info/manager/0001067983-berkshire-hathaway-inc"}
session = requests.Session()

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
    rows = html.split('<tr')
    # print(rows[2])
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

print(funds)