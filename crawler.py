from bs4 import BeautifulSoup
import requests
import os

#https://cp.hnonline.sk/vlak/spojenie/?date=16.11.2017&time=21%3a33&f=Ko%c5%a1ice&t=Bratislava+hl.st.&fc=100003&tc=100003&direct=true&submit=true
#https://cp.hnonline.sk/vlak/spojenie/?f=Ko%c5%a1ice&t=Bratislava+hl.st.&fc=100003&tc=100003&direct=true&submit=true

cp_url_with_datetime = "https://cp.hnonline.sk/{0}/spojenie/?data={1}&time={2}&f={3}&t={4}&direct=true&submit=true"
cp_url_actual_datetime = "https://cp.hnonline.sk/{0}/spojenie/?f={1}&t={2}&direct=true&submit=true"
#final_url = cp_url_with_datetime.format('vlak', '16.11.2017','15:00', 'Ko%c5%a1ice', 'Bratislava+hl.st.')
final_url = cp_url_actual_datetime.format('vlak', 'Ko%c5%a1ice', 'Bratislava+hl.st.')

r = requests.get(final_url)
#print(r.content)

#soup = BeautifulSoup(r.content, 'html.parser')
#print(soup)

filename_default = 'output'
filename_extention = '.txt'
filename = filename_default + "_0" + filename_extention;

counter = 1
while (os.path.exists(filename)):
    filename = filename_default + "_" + str(counter) + filename_extention
    counter += 1

with open(filename, 'wb') as outputfile:
    outputfile.write(r.content)
