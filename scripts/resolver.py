from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from classes import Link, Delay, RouteStop
import requests
import re


date_format = "%d.%m.%Y"
time_format = "%H:%M"

class Resolver():

    url_with_datetime = "https://cp.hnonline.sk/{0}/spojenie/?date={1}&time={2}&f={3}&t={4}&fc=100003&tc=100003&direct=true&submit=true"

    '''
    def __init__(self, station_f, station_t, trans='vlak'):
        self.trans = trans
        self.station_f = station_f
        self.station_t = station_t
    '''

    @staticmethod
    def create_url(trans, station_f, station_t, in_datetime):
        return Resolver.url_with_datetime.format(
            trans,
            in_datetime.strftime("%d.%m.%Y"),
            in_datetime.strftime("%H:%M"),
            station_f,
            station_t
        )

    @staticmethod
    def resolve_mainsite_datetime(station_f, station_t, in_datetime):
        url = Resolver.create_url(
            'vlak',
            station_f,
            station_t,
            in_datetime
        )
        return Resolver.__resolve_mainsite(url)

    @staticmethod
    def resolve_mainsite_now(station_f, station_t):
        url = Resolver.create_url(
            'vlak',
            station_f,
            station_t,
            datetime.now()
        )
        return Resolver.__resolve_mainsite(url)

    @staticmethod
    def resolve_mainsite_minutesback(station_f, station_t, minutes=0):
        minutes_back = abs(minutes)
        url = Resolver.create_url(
            'vlak',
            station_f,
            station_t,
            datetime.now() - timedelta(minutes=minutes_back)
        )
        return Resolver.__resolve_mainsite(url)

    @staticmethod
    def __resolve_mainsite(url):
        web_content = requests.get(url).content.decode('UTF-8')

        print("RESOLVING: " + url)

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
        new_link.train_name = " ".join(
            data_f[6].split('  ')[:-1]
        ).strip().replace('/', '')
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

        # Resolve links
        new_link.route_url, new_link.location_url = Resolver.__resolve_urls(
            [a.get('href') for a in tr_list[1].find_all('a')]
        )
        # Resolve 'draha' link
        #new_link.route = Resolver.__resolve_route(new_link)

        return new_link

    @staticmethod
    def __resolve_urls(href_list):
        route_url = ""
        location_url = ""

        root_link = 'https://cp.hnonline.sk'
        string_route = '/draha/'
        string_location = '/poloha/'
        for url_link in href_list:
            if (url_link.find(string_route) != -1):
                route_url = root_link + url_link
            elif (url_link.find(string_location) != -1):
                location_url = root_link + url_link

        return route_url, location_url

    @staticmethod
    def resolve_delay(link_object):
        if (not link_object.location_url):
            print("No location_url: " + link_object.train_name)
            return None

        print(
            "Resolving: " + link_object.train_name +
            " - " + link_object.location_url
        )

        # Download web page
        web_content = requests.get(
            link_object.location_url
        ).content.decode('UTF-8')

        # Remove everything after <!-- start PageEnd -->
        remove_before = '<!-- start PageEnd -->'
        remove_index = web_content.find(remove_before)
        # Invalid index
        if (remove_index == -1):
            link_object.location_url = ""
            return None

        trim_content = web_content[:remove_index]

        soup_data = BeautifulSoup(trim_content, 'html.parser')
        if (soup_data.table):
            data_list = list(filter(
                None,
                soup_data.table.text.split('\n')
            ))
            trim_list = [item[item.find(":") + 1: ] for item in data_list]
            # Invalid input data
            if (len(trim_list) != 4):
                link_object.location_url = ""
                return None

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
        if (not link_object.route_url):
            print("No route_url: " + link_object.train_name)
            return []

        print(
            "Resolve route: " + link_object.train_name +
            " - " + link_object.route_url
        )

        # Download web page
        web_content = requests.get(
            link_object.route_url
        ).content.decode('UTF-8')

        # Remove everything after <!-- start PageEnd -->
        remove_before = '<!-- start PageEnd -->'
        trim_content = web_content[:web_content.find(remove_before)]

        soup_data = BeautifulSoup(trim_content, 'html.parser')
        if (soup_data.table):
            stop_list = []
            for tr in soup_data.table.find_all('tr'):
                new_stop = Resolver.__resolve_stop(tr)
                if (new_stop):
                    stop_list.append(new_stop)

            return stop_list
        else:
            return []

    @staticmethod
    def __resolve_stop(tr):
        # 0 - station
        # 1 - time_arrival
        # 2 - time_departure
        # 3 - note
        # 4 - km
        # 5 - ''
        td_list = [
            td.text.replace(u'\xa0', '') for td in tr.find_all('td')
        ]
        if (len(td_list) == 6):
            return RouteStop(
                td_list[0].strip(),
                td_list[1],
                td_list[2],
                int(td_list[4])
            )
        else:
            return None
