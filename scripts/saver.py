from unidecode import unidecode
import json
import csv
import os


date_format = "%d.%m.%Y"
time_format = "%H:%M"

class Saver():

    @staticmethod
    def __check_link_directory(link_object):
        # Create datetime folder
        path = "logs/" + link_object.datetime_t.strftime(date_format)
        if (not os.path.exists(path)):
            os.mkdir(path)
        
        # Create route foler
        path += "/" + unidecode(link_object.get_route())
        if (not os.path.exists(path)):
            os.mkdir(path)

        # Create train_name folder
        path += "/" + unidecode(link_object.train_name)
        if (not os.path.exists(path)):
            os.mkdir(path)

        return path

    @staticmethod
    def save_link_info(link_object):
        # Create path
        path = Saver.__check_link_directory(link_object)
        path += "/info.json"

        # Save data
        json_file = open(path, 'w')
        json_file.write(
            json.dumps(
                link_object.get_json(),
                sort_keys=True,
                indent=4,
                separators=(',', ':')
            ),
        )
        json_file.close()

    @staticmethod
    def save_next_delay(link_object, next_delay):
        # Create path
        path = Saver.__check_link_directory(link_object)
        path += "/delay.csv"

        # Set settings
        file_open_type = "w" if (not os.path.exists(path)) else "a"
        csv_file = open(path, file_open_type)
        csv_writer = csv.writer(
            csv_file,
            delimiter=',',
            quotechar='\"',
            quoting=csv.QUOTE_MINIMAL
        )

        # Save data
        row = [
            str(next_delay.station_name),
            next_delay.regular_departure.strftime(
                date_format + " " + time_format
            ),
            next_delay.actual_departure.strftime(
                date_format + " " + time_format
            ),
            str(next_delay.delay)
        ]
        csv_writer.writerow(row)
        csv_file.close()
