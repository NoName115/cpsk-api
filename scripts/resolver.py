from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests


date_format = "%d.%m.%Y"
time_format = "%H:%M"

class Resolver():

    url_with_datetime = "https://cp.hnonline.sk/{0}/spojenie/?date={1}&time={2}&f={3}&t={4}&fc=100003&tc=100003&direct=true&submit=true"

    def __init__(self, station_f, station_t, trans='vlak'):
        self.trans = trans
        self.station_f = station_f
        self.station_t = station_t

    def create_url(self, in_datetime):
        return self.url_with_datetime.format(
            self.trans,
            in_datetime.strftime("%d.%m.%Y"),
            in_datetime.strftime("%H:%M"),
            self.station_f,
            self.station_t
        )

    def resolve_mainsite_datetime(self, in_datetime):
        url = self.create_url(in_datetime)
        return self.__resolve_mainsite(url)

    def resolve_mainsite_now(self):
        url = self.create_url(datetime.now())
        return self.__resolve_mainsite(url)

    def resolve_mainsite_minutesback(self, minutes):
        minutes_back = abs(minutes)
        url = self.create_url(
            datetime.now() - timedelta(minutes=minutes_back)
        )
        return self.__resolve_mainsite(url)

    @staticmethod
    def __resolve_mainsite(url):
        web_content = requests.get(url).content.decode('UTF-8')

        print("RES: " + url)

        # Remove everything between
        # <!-- zobrazeni vysledku start --> & <!-- zobrazeni vysledku end-->
        remove_before = '<!-- zobrazeni vysledku start -->'
        remove_after = '<!-- zobrazeni vysledku end-->'
        trim_content = web_content[
            web_content.find(remove_before): web_content.find(remove_after)
        ]

        soup_data = BeautifulSoup(trim_content, 'html.parser')

        # Resolver for all links from mainsite
        link_dict = {}
        for table in soup_data.find_all('table'):
            new_link = Resolver.__resolve_link_table(table)
            link_dict.update({
                new_link.train_name: new_link
            })

        return link_dict

    @staticmethod
    def __resolve_link_table(in_table):
        tr_list = in_table.find_all('tr')

        # 0 - ''
        # 1 - date_f
        # 2 - station_f
        # 3 - arrival_f
        # 4 - time_f
        # 5 - note_f
        # 6 - train_name + delay
        data_f = [
            td.text.replace(u'\xa0', u'')
            for td in tr_list[1].find_all('td')
        ]
        # 0 - ''
        # 1 - date_t / ''
        # 2 - station_t
        # 3 - time_t
        # 4 - departure_t
        # 5 - note_t
        # 6 - ''
        data_t = [
            td.text.replace(u'\xa0', u'')
            for td in tr_list[2].find_all('td')
        ]

        # Check data
        data_t[1] = data_t[1] if (data_t[1]) else data_f[1]

        # Create new link
        new_link = Link()
        new_link.train_name = " ".join(data_f[6].split('  ')[:-1]).strip()
        new_link.station_f = data_f[2].strip()
        new_link.station_t = data_t[2].strip()
        new_link.datetime_f = datetime.strptime(
            data_f[1] + "2017" + data_f[4],
            date_format + time_format
        )
        new_link.datetime_t = datetime.strptime(
            data_t[1] + "2017" + data_t[3],
            date_format + time_format
        )
        '''
        new_link.datetime_arrival_f = datetime.strptime(
            #TODO
        )
        new_link.datetime_departure_t = datetime.strptime(
            #TODO
        )
        '''
        new_link.note_f = data_f[5]
        new_link.note_t = data_t[5]

        new_link.route_url, new_link.location_url = Resolver.__resolve_urls(
            [a.get('href') for a in tr_list[1].find_all('a')]
        )

        return new_link

    @staticmethod
    def __resolve_urls(href_list):
        route_url = ""
        location_url = ""

        root_link = 'https://cp.hnonline.sk'
        string_route = '/draha/'
        string_location = '/poloha/'
        for link in href_list:
            if (link.find(string_route) != -1):
                route_url = root_link + link
            elif (link.find(string_location) != -1):
                location_url = root_link + link

        return route_url, location_url

    @staticmethod
    def resolve_delay(link_object):
        if (not link_object.location_url):
            print("No location_url")
            return None

        # Download web page
        web_content = requests.get(
            link_object.location_url
        ).content.decode('UTF-8')

        # Remove everything after <!-- start PageEnd -->
        remove_before = '<!-- start PageEnd -->'
        trim_content = web_content[:web_content.find(remove_before)]

        soup_data = BeautifulSoup(trim_content, 'html.parser')
        if (soup.table):
            data_list = list(filter(
                None,
                soup_data.table.text.split('\n')
            ))
            trim_list = [item[item.find(":") + 1: ] for item in data_list]

            # Create delay class
            new_delay = Delay(
                trim_list[0],
                datetime.strptime(
                    link_object.datetime_f.strftime(
                        date_format
                    ) + trim_list[1],
                    date_format + time_format
                ),
                datetime.strptime(
                    trim_list[2],
                    date_format + " " + time_format
                ),
                int(re.search(r'\d+', trim_list[3]).group())
            )
            return new_delay
        else:
            return None

        @staticmethod
        def resolve_route(link_object):
            # TODO
            pass
