from bs4 import BeautifulSoup
import re


class Spojenie():

    def __init__(self, date_f, city_f, time_a, time_f, train, delay, delay_info):
        self.date_from = date_f
        self.city_from = city_f
        self.time_arrival = time_a
        self.time_from = time_f
        self.train = train
        self.delay = delay

        # Aktualne bez meskania, Ocakava sa meskanie
        self.delay_info = ""

def parse_tr(tr):
    print(tr.text)

    # Dátum | (Odkiaľ/Prestup/Kam | Prích. | Odch. | Pozn. | Spoje + meskanie)
    parsed_info = re.search(
        r'(\d?\d\.\d?\d\.)(.*)',
        tr.text
    )

    date_from = parsed_info.group(1)
    rest_string = parsed_info.group(2).replace(u'\xa0', u' ').split('  ')

    print(parsed_info.groups())
    print("REST: " + str(rest_string) + "\n")

    # Train name
    train = rest_string[2] if (rest_string[1].find(':') != -1) else rest_string[1]

    # Delay solver
    delay = 0
    delay_info = ""
    last_index = len(rest_string) - 1
    if (rest_string[last_index].find("meška")):
        delay_info = rest_string[last_index].strip()

    delay_re = re.search(r'\d+', rest_string[last_index])
    if (delay_re):
        delay = int(delay_re.group())

    # time_arrival, time_from & city_from solver
    time_arrival = ''
    time_from = ''
    city_from = ''
    if (rest_string[1].find(':') != -1):
        city_from = rest_string[0]
        time_from = rest_string[1]
    else:
        splited = rest_string[0].split()
        city_from = splited[0]
        index_dots = splited[1].find(':')
        time_arrival = splited[1][:index_dots + 3]
        time_from = splited[1][index_dots + 3: ]

    print("FROM DATE: " + str(date_from))
    print("FROM CITY: " + str(city_from))
    print("TIME ARRIVAL: " + str(time_arrival))
    print("FROM TIME: " + str(time_from))
    print("TRAIN: " + str(train))
    print("DELAY: " + str(delay))
    print("DELAY_INFO: " + str(delay_info))

    # Link to draha & poloha
    for aa in tr.find_all('a'):
        print(aa.get('href'))

open_filename = 'output_5.txt'

with open(open_filename, 'r') as inputfile:
    data = inputfile.read()

# Remove everything between '<!-- zobrazeni vysledku start -->' & <!-- zobrazeni vysledku end-->
remove_before = '<!-- zobrazeni vysledku start -->'
remove_after = '<!-- zobrazeni vysledku end-->'
trim_data = data[data.find(remove_before): data.find(remove_after)]

soup = BeautifulSoup(trim_data, 'html.parser')

# Parse html
for table in soup.find_all('table'):
    print("-------------------------")
    tr_list = table.find_all('tr')
    parse_tr(tr_list[1])
