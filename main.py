from bs4 import BeautifulSoup
from requests import get

url = 'https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two'

page = get(url)
bs = BeautifulSoup(page.content, 'html.parser')

for offer in bs.find_all(attrs={"data-cy": "l-card"}):
    footer = offer.find(attrs={"data-testid": "location-date"})
    footerString = offer.find(attrs={"data-testid": "location-date"}).get_text()
    location = footerString.split(' - ')[0]
    dateList = (footerString.split(' - ')[1]).split()[-3:]
    date = ' '.join(dateList)
    title = offer.find('h6').get_text().strip()
    price = offer.find(attrs={"data-testid": "ad-price"}).get_text().strip()
    size = footer.find_next('p').get_text()

    print(date) 
    print(title)   
    print(location)
    print(size)
    print(price)
    print()