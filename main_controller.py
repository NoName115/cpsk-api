from bs4 import BeautifulSoup
from classes import Spojenie
import re
import time


cp_url_actual_datetime = "https://cp.hnonline.sk/{0}/spojenie/?f={1}&t={2}&direct=true&submit=true"
station_from = 'Ko%c5%a1ice'
station_to = 'Bratislava+hl.st.'
transport = 'vlak'

def download_mainsite(link_database):
    # Download website
    final_url = cp_url_actual_datetime.format(transport, station_from, station_to)
    return requests.get(final_url)

def load_from_file_mainsite(filename):
    with open(filename, 'r') as inputfile:
        return inputfile.read()

def resolve_mainsite(website_content):
    # Remove everything between '<!-- zobrazeni vysledku start -->' & <!-- zobrazeni vysledku end-->
    remove_before = '<!-- zobrazeni vysledku start -->'
    remove_after = '<!-- zobrazeni vysledku end-->'
    trim_data = website_content[
        website_content.find(remove_before): website_content.find(remove_after)
    ]
    soup = BeautifulSoup(
        trim_data,
        'html.parser'
    )

    all_links = {}
    # Parse links
    for table in soup.find_all('table'):
        new_link = Spojenie(table.find_all('tr'))
        new_link.resolve_main_data()
        all_links.update({
            new_link.train_name: new_link
        })
        # DEBUG
        #print(new_link)

    return all_links

delay_resolve_sleeptime = 5 #5*60
mainsite_resolve_sleeptime = 30 #30*60

actual_links = {}
while (1):
    site_content = load_from_file_mainsite('testdata.txt')
    new_links = resolve_mainsite(site_content)

    for train_name, train_object in new_links.items():
        if (train_name not in actual_links):
            actual_links.update({
                train_name: train_object
            })
            print("Nove spojenie " + train_name)
        else:
            print("Spojenie " + train_name + " uz existuje!!!")

    slept_time = 0
    while (slept_time < mainsite_resolve_sleeptime):
        print("--------- RESOLVE ---------")

        for train_name, link_object in new_links.items():
            link_object.resolve_delay()

        time.sleep(delay_resolve_sleeptime)
        slept_time += delay_resolve_sleeptime
