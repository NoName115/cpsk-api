from saver import Saver
from datetime import timedelta


date_format = "%d.%m.%Y"
time_format = "%H:%M"

class Link():

    def __init__(self):
        # Main data
        self.train_name = ""
        self.station_f = ""
        self.station_t = ""
        self.datetime_f = ""
        self.datetime_t = ""

        # Info data
        self.datetime_arrival_f = ""
        self.datetime_departure_t = ""
        self.note_f = ""
        self.note_t = ""

        # Urls
        self.route_url = ""
        self.location_url = ""

        # Delays
        self.delays = []
        # Route stops
        self.route = []

    def add_route(self, route_list):
        self.route = route_list

    def add_delay(self, new_delay):
        if (not new_delay):
            return
        self.delays.append(new_delay)
        Saver.save_next_delay(self, new_delay)

    def get_real_datetime_t(self):
        return self.datetime_t + timedelta(minutes=self.delays[-1].delay) \
            if (self.delays) else self.datetime_t

    def is_route_resolved(self):
        return self.route

    def get_route(self):
        return (self.station_f + "-->" + self.station_t)

    def get_json(self):
        json_dict = {
            'train_name': str(self.train_name),
            'station_from': str(self.station_f),
            'station_to': str(self.station_t),
            'datetime_from': self.datetime_f.strftime(
                date_format + " " + time_format
            ),
            'datetime_to': self.datetime_t.strftime(
                date_format + " " + time_format
            ),
            #'time_arrival_from': str(self.time_arrival_from),
            #'time_departure_to': str(self.time_departure_to),
            'route_url': str(self.route_url),
            'location_url': str(self.location_url),
            'route': [
                route_stop.get_json() for route_stop in self.route
            ]
        }
        return json_dict

    def get_string(self):
        return str(self)

    def __str__(self):
        return_string = (
            self.station_f +
            " (" + str(self.datetime_f) + ")" +
            " --> " + str(self.station_t) +
            "(" + str(self.datetime_t) + ")\n"
        )

        return_string += "TRAIN:\t\t" + str(self.train_name) + "\n"
        return_string += "ROUTE URL:\t" + str(self.route_url) + "\n"
        return_string += "LOCATION URL:\t" + str(self.location_url) + "\n"
        return_string += "ROUTE:\n"

        route_string = ""
        for route_stop in self.route:
            route_string += "\t" + str(route_stop)
        return_string += route_string

        return_string += "DELAYS:\n"

        delay_string = ""
        for delay_object in self.delays:
            delay_string += "\t" + str(delay_object)
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
            self.station_name + "  " + str(self.regular_departure) + " - " +
            str(self.actual_departure) + "(" + str(self.delay) + ")\n"
        )


class RouteStop():

    def __init__(self, station, time_arrival, time_departure, km):
        self.station = station
        self.time_arrival = time_arrival
        self.time_departure = time_departure
        self.km = km

    def __str__(self):
        return (
            '{0:25} ({1:5} - {2:5}) {3:5}km\n'.format(
                self.station,
                str(self.time_arrival),
                str(self.time_departure),
                str(self.km)
            )
        )

    def get_json(self):
        json_dict = {
            'station': self.station,
            'time_arrival': self.time_arrival,
            'time_departure': self.time_departure,
            'km': self.km
        }
        return json_dict
