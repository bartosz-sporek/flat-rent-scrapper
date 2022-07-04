from bs4 import BeautifulSoup
from requests import get
import sqlite3
from sys import argv
import babel.dates
import datetime
from datetime import date

MAIN_OLX = "https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two"
PAGES_OLX = "https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two&page="
BASE_OLX = "https://www.olx.pl"
MONTHS_OLX = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']

db = sqlite3.connect('data.db')
cursor = db.cursor()

if len(argv) > 1 and argv[1] == 'setup':
    cursor.execute('''CREATE TABLE offers (date TEXT, name TEXT UNIQUE, city TEXT, size REAL, price REAL, link TEXT UNIQUE);''')
    quit()

page = get(MAIN_OLX)
bs = BeautifulSoup(page.content, 'html.parser')
lastPage = bs.select('ul.pagination-list li:nth-of-type(5) > a:nth-of-type(1)')[0]['href']
lp = lastPage.rsplit('=', 1)[-1]
count = 0
pageNum = 0

for i in range(int(lp)):
    
    pageNum += 1
    # Fix incrementing count
    print(f"Gathering {str(pageNum)}/{str(lp)}")

    count+=1
    url = PAGES_OLX + str(count)
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

        if month == MONTHS_OLX[0]:
            month = "01"
        elif month == MONTHS_OLX[1]:
            month = "02"
        elif month == MONTHS_OLX[2]:
            month = "03"
        elif month == MONTHS_OLX[3]:
            month = "04"
        elif month == MONTHS_OLX[4]:
            month = "05"
        elif month == MONTHS_OLX[5]:
            month = "06"
        elif month == MONTHS_OLX[6]:
            month = "07"
        elif month == MONTHS_OLX[7]:
            month = "08"
        elif month == MONTHS_OLX[8]:
            month = "09"
        elif month == MONTHS_OLX[9]:
            month = "10"
        elif month == MONTHS_OLX[10]:
            month = "11"
        elif month == MONTHS_OLX[11]:
            month = "12"

        if "Dzisiaj" in dateLong:
            dateLong = dateLong.replace(dateLong, babel.dates.format_date(now, 'yyyy/MM/dd', locale='pl_PL'))
        else:
            dateLong = f'{year}/{month}/{day}'

        title = offer.find('h6').get_text().strip()
        price = offer.find(attrs={"data-testid": "ad-price"}).get_text().strip()
        size = footer.find_next('p').get_text()
        linkEnding = offer.find('a')['href']
        link = BASE_OLX + linkEnding

        try:
            cursor.execute('INSERT INTO offers VALUES (?, ?, ?, ?, ?, ?)', (dateLong, title, location, size, price, link))
        except sqlite3.IntegrityError:
            continue

        db.commit()

db.close()