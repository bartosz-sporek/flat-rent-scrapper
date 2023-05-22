from bs4 import BeautifulSoup
from requests import get
import csv
import os
from sys import argv
import babel.dates
import datetime

BASE_OLX = "https://www.olx.pl"
MAIN_OLX = f"{BASE_OLX}/d/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bprivate_business%5D=private&search%5Bfilter_float_price:from%5D=2300&search%5Bfilter_float_price:to%5D=2700&search%5Bfilter_enum_furniture%5D%5B0%5D=yes&search%5Bfilter_float_m:from%5D=35&search%5Bfilter_enum_rooms%5D%5B0%5D=two"
PAGES_OLX = f"{MAIN_OLX}&page="
MONTHS_OLX = {
    'stycznia': '01',
    'lutego': '02',
    'marca': '03',
    'kwietnia': '04',
    'maja': '05',
    'czerwca': '06',
    'lipca': '07',
    'sierpnia': '08',
    'września': '09',
    'października': '10',
    'listopada': '11',
    'grudnia': '12'
}

page = get(MAIN_OLX)
bs = BeautifulSoup(page.content, 'html.parser')
lastPage = bs.select('ul.pagination-list li:nth-of-type(5) > a')[0].text
numOfOffersAdded = 0

existing_rows = set()

# Read existing rows from the CSV file
if os.path.exists('flats.csv'):
    with open('flats.csv', 'r', encoding="utf-8", newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            existing_rows.add(tuple(row))

with open('flats.csv','a', encoding="utf-8", newline='') as f1: 
    writer=csv.writer(f1, delimiter='\t')
    
    # Skip writing the header if the file is not empty
    if os.stat('flats.csv').st_size == 0:
        writer.writerow(['Data', 'Tytuł', 'Lokalizacja', 'Rozmiar', 'Cena', 'Link'])

    for page_num in range(1, int(lastPage)+1):

        print(f"Gathering {page_num}/{lastPage}")

        url = PAGES_OLX + str(page_num)
        rq = get(url)
        bs = BeautifulSoup(rq.content, 'html.parser')

        for offer in bs.find_all(attrs={"data-cy": "l-card"}):
            footer = offer.find(attrs={"data-testid": "location-date"})
            footerString = offer.find(attrs={"data-testid": "location-date"}).get_text()
            try:
                location = (footerString.split(' - ')[0]).split(', ')[1]
            except IndexError:
                location = (footerString.split(' - ')[0])
            dateList = (footerString.split(' - ')[1]).split()[-3:]
            dateLong = ' '.join(dateList)
            now = datetime.datetime.now()
            day, month, year = dateLong.split(' ')

            if month in MONTHS_OLX:
                month = MONTHS_OLX[month]

            if "Dzisiaj" in dateLong:
                dateLong = dateLong.replace(dateLong, babel.dates.format_date(now, 'yyyy/MM/dd', locale='pl_PL'))
            else:
                dateLong = f'{year}/{month}/{day}'

            title = offer.find('h6').get_text().strip()
            price = offer.find(attrs={"data-testid": "ad-price"}).next_element.strip()
            size = footer.find_next('span').get_text()
            linkEnding = offer.find('a')['href']
            link = BASE_OLX + linkEnding
            if "otodom" in link:
                link = linkEnding

            row_data = [dateLong, title, location, size, price, link]

            if tuple(row_data) not in existing_rows:
                writer.writerow(row_data)
                numOfOffersAdded += 1
                existing_rows.add(tuple(row_data))

print(f"{numOfOffersAdded} of the new offers were added.")