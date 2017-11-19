from bs4 import BeautifulSoup
import re

open_filename = 'draha_test.txt'

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
    new_link = Spojenie(table.find_all('tr'))
    new_link.resolve_train_name()
    #print(new_link)
