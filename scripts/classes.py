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

    def add_delay(self, new_delay):
        if (not new_delay):
            return
        self.delays.append(new_delay)
        Saver.save_next_delay(self, new_delay)

    def get_real_datetime_t(self):
        return self.datetime_t + timdelta(minutes=self.delays[-1]) \
            if (self.delays) else self.datetime_t

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
        return_string += 'LOCATION URL:\t' + str(self.location_url) + "\n"

        delay_string = "\n"
        for delay_object in self.delays:
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
            self.station_name + "  " + str(self.regular_departure) + " - " +
            str(self.actual_departure) + "(" + str(self.delay) + ")\n"
        )
