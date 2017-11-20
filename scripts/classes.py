from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import json
import re
import os


date_format = "%d.%m.%Y"
time_format = "%H:%M"

class Spojenie():

    def __init__(self, tr_list):
        self.tr_list = tr_list

        self.city_from = ""
        self.city_to = ""

        self.time_arrival_from = ""
        self.time_departure_to = ""

        self.train_name = ""

        # Urls
        self.route_url = ""
        self.location_url = ""

        # Delay list
        self.delay_list = []

    def update_info(self, other_spojenie):
        self.route_url = other_spojenie.route_url
        self.location_url = other_spojenie.location_url

        Saver.save_link_info(self)

    def get_actual_arrival(self):
        if (self.delay_list):
            last_delay = self.delay_list[-1].delay
            actual_arrival = self.datetime_to + timedelta(
                minutes=last_delay
            )
            return actual_arrival
        else:
            return self.datetime_to

    def resolve_main_data(self):
        self.resolve_first_tr()
        self.resolve_second_tr()

    def resolve_first_tr(self):
        parsed_info = re.search(
            r'(\d?\d\.\d?\d\.)(.*)',
            self.tr_list[1].text
        )

        date_from = parsed_info.group(1)
        rest_string = parsed_info.group(2).replace(u'\xa0', u' ').split('  ')

        # rest_string ->
        # ['city_from', 'time_from', 'train', '', '', '', 'delay']
        # ['city_from time_arrival_from time_from', 'train', '', '', '', 'delay']

        self.train_name = self.resolve_train_name(
            rest_string[1:3]
        )
        self.time_arrival_from, time_from, self.city_from = self.resolve_time_and_city_from(
            rest_string[0:2]
        )
        self.route_url, self.location_url = self.resolve_urls(
            self.tr_list[1].find_all('a')
        )
        self.datetime_from = datetime.strptime(
            date_from + "2017 " + time_from, date_format + " " + time_format
        )

    def resolve_second_tr(self):
        # dd.mm.stanica hh:mm
        # stanica hh:mm
        parsed_info = re.search(
            r'(\d?\d\.\d?\d\.)(.*)',
            self.tr_list[2].text
        )

        if (parsed_info):
            date_to = parsed_info.group(1)
            self.city_to, time_to, self.time_departure_to = self.resolve_time_and_city_to(
                parsed_info.group(2).split()
            )
        else:
            date_to = self.datetime_from.strftime(date_format[:-2])
            self.city_to, time_to, self.time_departure_to = self.resolve_time_and_city_to(
                self.tr_list[2].text.split()
            )

        self.datetime_to = datetime.strptime(
            date_to + "2017 " + time_to, date_format + " " + time_format
        )

    def resolve_delay(self):
        print("Resolving delay: " + self.train_name)

        if (not self.location_url):
            print("No location_url in " + self.train_name)
            return

        result = requests.get(self.location_url)
        website_content = result.content.decode('UTF-8')

        #website_content = open('location_test.txt').read()

        # Remove everything after <!-- start PageEnd -->
        remove_before = '<!-- start PageEnd -->'
        trim_data = website_content[:website_content.find(remove_before)]

        soup = BeautifulSoup(trim_data, 'html.parser')
        if (soup.table):
            list_string = list(filter(
                None,
                soup.table.text.split('\n')
            ))
            trim_list = [item[item.find(":") + 1: ] for item in list_string]

            # Create delay class and add to dictionary
            new_delay = Delay(
                trim_list[0],
                trim_list[1],
                trim_list[2],
                int(re.search(r'(\d+)', trim_list[3]).group()),
            )
            self.delay_list.append(new_delay)

            # Save delay data to CSV
            Saver.save_new_delay(self, new_delay)

    @staticmethod
    def resolve_time_and_city_to(rest_list):
        city_to = " ".join(rest_list[:-1])
        time_to = "".join(rest_list[-1:])
        time_departure_to = ""

        if (time_to.count(":") == 2):
            index_dots = time_to.find(":")
            time_departure_to = time_to[index_dots + 3: ]
            time_to = time_to[:index_dots + 3]

        return city_to, time_to, time_departure_to

    @staticmethod
    def resolve_train_name(rest_list):
        train_name = rest_list[1] if (rest_list[0].find(':') != -1) else rest_list[0]
        return train_name.replace('/', '')

    @staticmethod
    def resolve_time_and_city_from(rest_list):
        time_arrival_from = ""
        time_from = ""
        city_from = ""
        if (rest_list[1].find(':') != -1):
            city_from = rest_list[0]
            time_from = rest_list[1]
        else:
            splited = rest_list[0].split()
            city_from = splited[0]
            index_dots = splited[1].find(":")
            time_arrival_from = splited[1][:index_dots + 3]
            time_from = splited[1][index_dots + 3: ]  

        return time_arrival_from, time_from, city_from

    @staticmethod
    def resolve_urls(a_component_list):
        route_url = ""
        location_url = ""

        root_link = 'https://cp.hnonline.sk'
        string_route = '/draha/'
        string_location = '/poloha/'
        for a in a_component_list:
            link = a.get('href')
            if (link.find(string_route) != -1):
                route_url = root_link + link
            elif (link.find(string_location) != -1):
                location_url = root_link + link

        return route_url, location_url

    def __str__(self):
        return_string = (
            self.city_from +
            " (" + str(self.datetime_from) + ")" +
            " --> " + str(self.city_to) +
            "(" + str(self.datetime_to) + ")\n"
        )

        return_string += "ARRIVAL TIME:\t" + str(self.time_arrival_from) + "\n"
        return_string += "DEPARTURE TIME:\t" + str(self.time_departure_to) + "\n"
        return_string += "TRAIN:\t\t" + str(self.train_name) + "\n"
        return_string += "ROUTE URL:\t" + str(self.route_url) + "\n"
        return_string += 'LOCATION URL:\t' + str(self.location_url) + "\n"

        delay_string = "\n"
        for station_name, delay_object in self.delay_dict.items():
            delay_string += str(delay_object)

        return_string += delay_string

        return return_string


class Delay():

    def __init__(self, st_name, reg_dep, act_dep, delay):
        self.station_name = st_name
        self.regular_departure = reg_dep
        self.actual_departure = act_dep
        self.delay = delay

    def __str__(self):
        return (
            self.station_name + " " + str(self.regular_departure) + "\n" +
            str(self.actual_departure) + "(" + str(self.delay) + ")\n"
        )


class Saver():

    @staticmethod
    def check_link_directory(link):
        path = "../logs/" + link.datetime_to.strftime(date_format) #datetime.now().date().strftime("%d.%m.%Y")
        # Create datetime folder
        if (not os.path.exists(path)):
            os.mkdir(path)

        path += "/" + link.train_name
        # Create link folder
        if (not os.path.exists(path)):
            os.mkdir(path)

        return path

    @staticmethod
    def save_link_info(link):
        path = Saver.check_link_directory(link) + "/info.json"
        json_file = open(path, 'w')
        json_file.write(
            json.dumps(
                {
                    'train_name': str(link.train_name),
                    'city_from': str(link.city_from),
                    'city_to': str(link.city_to),
                    'datetime_from': str(link.datetime_from),
                    'datetime_to': str(link.datetime_to),
                    'time_arrival_from': str(link.time_arrival_from),
                    'time_departure_to': str(link.time_departure_to),
                    'route_url': str(link.route_url),
                    'location_url': str(link.location_url),
                },
                sort_keys=True,
                indent=4,
                separators=(',', ':')
            )
        )
        json_file.close()

    @staticmethod
    def save_new_delay(link, new_delay):
        path = Saver.check_link_directory(link) + "/delay.csv"
        file_open_type = "w" if (not os.path.exists(path)) else "a"
        csv_file = open(path, file_open_type)
        csv_file.write(
            str(new_delay.station_name) + "," +
            str(new_delay.regular_departure) + "," +
            str(new_delay.actual_departure) + "," +
            str(new_delay.delay) + "\n"
        )
        csv_file.close()
