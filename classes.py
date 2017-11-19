import re


class Spojenie():

    def __init__(self, tr_list):
        self.tr_list = tr_list

        self.date_from = ""
        self.date_to = ""

        self.city_from = ""
        self.city_to = ""

        self.time_arrival = ""
        self.time_from = ""
        self.time_to = ""

        self.train_name = ""

        # Urls
        self.route_url = ""
        self.location_url = ""

        # Delay dictionary, key - station, value - Class delay
        self.delay_dict = {}

    def resolve_main_data(self):
        self.resolve_first_tr()
        self.resolve_second_tr()

    def resolve_first_tr(self):
        parsed_info = re.search(
            r'(\d?\d\.\d?\d\.)(.*)',
            self.tr_list[1].text
        )

        self.date_from = parsed_info.group(1)
        rest_string = parsed_info.group(2).replace(u'\xa0', u' ').split('  ')

        # rest_string ->
        # ['city_from', 'time_from', 'train', '', '', '', 'delay']
        # ['city_from time_arrival time_from', 'train', '', '', '', 'delay']

        self.train_name = self.resolve_train_name(
            rest_string[1:3]
        )
        self.time_arrival, self.time_from, self.city_from = self.resolve_time_and_city_from(
            rest_string[0:2]
        )
        self.route_url, self.location_url = self.resolve_urls(
            self.tr_list[1].find_all('a')
        )

    def resolve_second_tr(self):
        # dd.mm.stanica hh:mm
        # stanica hh:mm
        parsed_info = re.search(
            r'(\d?\d\.\d?\d\.)(.*)',
            self.tr_list[2].text
        )

        if (parsed_info):
            self.date_to = parsed_info.group(1)
            self.city_to, self.time_to = self.resolve_time_and_city_to(
                parsed_info.group(2).split()
            )
        else:
            self.date_to = self.date_from
            self.city_to, self.time_to = self.resolve_time_and_city_to(
                self.tr_list[2].text.split()
            )

    # TODO
    def resolve_delay(self):
        print("RESOLVING DELAY...")

    @staticmethod
    def resolve_time_and_city_to(rest_list):
        return "".join(rest_list[:-1]), "".join(rest_list[-1:])

    @staticmethod
    def resolve_train_name(rest_list):
        return (
            rest_list[1] if (rest_list[0].find(':') != -1) else rest_list[0]
        )

    @staticmethod
    def resolve_time_and_city_from(rest_list):
        time_arrival = ""
        time_from = ""
        city_from = ""
        if (rest_list[1].find(':') != -1):
            city_from = rest_list[0]
            time_from = rest_list[1]
        else:
            splited = rest_list[0].split()
            city_from = splited[0]
            index_dots = splited[1].find(":")
            time_arrival = splited[1][:index_dots + 3]
            time_from = splited[1][index_dots + 3: ]  

        return time_arrival, time_from, city_from

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

    '''
    @staticmethod
    def resolve_delay(delay_data):
        delay_info = delay_data.strip() if (delay_data.find("mešká")) else ""

        delay_re = re.search(r'\d+', delay_data)
        delay = int(delay_re.group()) if (delay_re) else 0

        return delay, delay_info
    '''

    def __str__(self):
        return_string = (
            self.city_from +
            " (" + str(self.date_from) + " " + str(self.time_from) + ")" +
            " --> " + str(self.city_to) +
            "(" + str(self.date_to) + " " + str(self.time_to) + ")\n"
        )

        return_string += "ARRIVAL TIME:\t" + str(self.time_arrival) + "\n"
        return_string += "TRAIN:\t\t" + str(self.train_name) + "\n"
        return_string += "ROUTE URL:\t" + str(self.route_url) + "\n"
        return_string += 'LOCATION URL:\t' + str(self.location_url) + "\n"

        return return_string


class Delay():

    def __init__(self):
        self.station_name = ""
        self.regular_departure = ""
        self.actual_departure = ""
        self.delay = 0
