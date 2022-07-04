from bs4 import BeautifulSoup
from requests import get
import sqlite3
from sys import argv
import babel.dates
import datetime
from datetime import date




db = sqlite3.connect('data.db')
cursor = db.cursor()

if len(argv) > 1 and argv[1] == 'setup':
    cursor.execute('''CREATE TABLE offers (date TEXT, name TEXT, city TEXT, size REAL, price REAL)''')
    quit()

page = get("https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two")
bs = BeautifulSoup(page.content, 'html.parser')
lastPage = bs.select('ul.pagination-list li:nth-of-type(5) > a:nth-of-type(1)')[0]['href']
lp = lastPage.rsplit('=', 1)[-1]
count = 0

for i in range(int(lp)):
    count+=1
    url = 'https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two&page='+str(count)
    rq = get(url)
    bs = BeautifulSoup(rq.content, 'html.parser')

    for offer in bs.find_all(attrs={"data-cy": "l-card"}):
        footer = offer.find(attrs={"data-testid": "location-date"})
        footerString = offer.find(attrs={"data-testid": "location-date"}).get_text()
        location = footerString.split(' - ')[0]
        dateList = (footerString.split(' - ')[1]).split()[-3:]
        dateLong = ' '.join(dateList)
        now = datetime.datetime.now()
        day = dateLong.split(' ')[0]
        month = dateLong.split(' ')[1]
        year = dateLong.split(' ')[2]

        match month:
            case 'stycznia':
                month = "1"
            case 'lutego':
                month = "2"
            case 'marca':
                month = "3"
            case 'kwietnia':
                month = "4"
            case 'maja':
                month = "5"
            case 'czerwca':
                month = "6"
            case 'lipca':
                month = "7"
            case 'sierpnia':
                month = "8"
            case 'września':
                month = "9"
            case 'października':
                month = "10"
            case 'listopada':
                month = "11"
            case 'grudnia':
                month = "12"

        if "Dzisiaj" in dateLong:
            dateLong = dateLong.replace(dateLong, babel.dates.format_date(now, 'yyyy/MM/dd', locale='pl_PL'))
        else:
            dateLong = f'{year}/0{month}/{day}'

        cursor.execute('''SELECT *
        FROM offers
        ORDER BY date DESC;''')

        title = offer.find('h6').get_text().strip()
        price = offer.find(attrs={"data-testid": "ad-price"}).get_text().strip()
        size = footer.find_next('p').get_text()
        
        cursor.execute('INSERT INTO offers VALUES (?, ?, ?, ?, ?)', (dateLong, title, location, size, price))

        db.commit()

db.close()