import requests
from bs4 import BeautifulSoup
import re
import pandas as pd



items = pd.read_csv(input.csv)
df = pd.DataFrame(columns=["ModelNum", "TotalPrice", "BasePrice", "ShippingPrice", "URL"])
for _ in items:
    URL = ("https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313.TR1.TRC0.A0.H0.X"
        +_+".TRS0&_nkw="
        +_+"&_sacat=0&LH_TitleDesc=0&_sop=15&_osacat=0&_odkw=dell+latitude&LH_BIN=1&rt=nc")
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    
    listings = soup.findAll('li', id=lambda x: x and x.startswith('srp-river-results-listing'))
    prices = [item.find('span', attrs = {'class':'s-item__price'}) for item in listings]
    shipping = [item.find('span', attrs = {'class':'s-item__shipping s-item__logisticsCost'}) for item in listings]
    num_prices = list(prices)
    shipping_prices = list(shipping)
    links = list(listings)
    for item in range(len(links)):
        links[item] = re.sub(r'.*href="https://www.ebay.com/itm/','https://www.ebay.com/itm/', str(links[item]))
        links[item] = re.sub(r'LH_BIN=1.*','LH_BIN=1', str(links[item]))
    for _ in range(len(num_prices)):
        num_prices[_] = re.sub(r'.*\$', '', str(num_prices[_]))
        num_prices[_] = re.sub(r'</.*', '', str(num_prices[_]))
    for _ in range(len(shipping_prices)):
        if "Free Shipping" in str(shipping_prices[_]):
            #shipping_prices[_] = re.sub(r'.*Free', 'Free', str(shipping[_]))
            shipping_prices[_] = '0' #re.sub(r'Shipping.*', 'Shipping', str(shipping[_]))
        else:
            shipping_prices[_] = re.sub(r'.*\$', '', str(shipping_prices[_]))
            shipping_prices[_] = re.sub(r' ship.*', '', str(shipping_prices[_]))
        if shipping_prices[_] == None:
            shipping_prices[_] = '0'
        if shipping_prices[_] == 'None':
            shipping_prices[_] = '0'

    #shipping_prices[_] = float(shipping_prices[_])
    num_prices = [float(_) for _ in num_prices]
    shipping_prices = [float(_) for _ in shipping_prices]
    total_prices = [num_prices[_] + shipping_prices[_] for _ in range(len(num_prices))]
    model_num = [num]*len(total_prices)
    #table = [list(a) for a in zip(model_num, total_prices, num_prices, shipping_prices)]
    newframe = pd.DataFrame(total_prices, columns=['TotalPrice'])
    newframe['ModelNum'] = model_num
    newframe['ShippingPrice'] = shipping_prices
    newframe['BasePrice'] = num_prices
    newframe['URL'] = links
    #flattened = [val for sublist in table for val in sublist]
    df = pd.concat([df, newframe])
pd.DataFrame.to_csv(df, "output.csv")
