from resolver import Resolver
from datetime import datetime
from saver import Saver
import time
import sys
import os


def print_links(all_links):
    for train_name, link_object in all_links.items():
        print(link_object)

def add_update_newlinks(all_links, new_links):
    for train_name, link_object in new_links.items():
        if (train_name not in all_links):
            all_links.update({
                train_name: link_object
            })
            link_object.add_route(Resolver.resolve_route(link_object))
            Saver.save_link_info(link_object)
            print("Nove spojenie: " + train_name)
        else:
            actual_link = all_links[train_name]
            if (not actual_link.location_url
               and link_object.location_url):
                actual_link.location_url = link_object.location_url
                Saver.save_link_info(actual_link)
                print("Location_link update: " + train_name)

            '''
            if (not actual_link.is_route_resolved()):
                actual_link.add_route(Resolver.resolve_route(actual_link))
                Saver.save_link_info(actual_link)
                print("Route_link update: " + train_name)
            '''


def resolve_few_hours_back(station_f, station_t, hours):
    all_new_links = {}
    for i in range(hours, 0, -2):
        new_links = Resolver.resolve_mainsite_minutesback(station_f, station_t, i*60)
        add_update_newlinks(all_new_links, new_links)
    return all_new_links


update_time = 5*60
actual_links = {}

new_links = resolve_few_hours_back('Košice', 'Bratislava+hl.st.', 6)
add_update_newlinks(actual_links, new_links)
new_links = resolve_few_hours_back('Bratislava', 'Brno', 4)
add_update_newlinks(actual_links, new_links)

while (1):
    try:
        print("\n\n--------- START RESOLVE ---------")
        print("------ " + str(datetime.now()))

        # Resolve Kosice -> Bratislava link
        links = Resolver.resolve_mainsite_now('Košice', 'Bratislava+hl.st.')
        add_update_newlinks(actual_links, links)

        # Resolve Bratislava -> Brno link
        links = Resolver.resolve_mainsite_now('Bratislava', 'Brno')
        add_update_newlinks(actual_links, links)

        print("--------- CHECKING DATA ---------")
        train_to_remove = set()
        for train_name, link_object in actual_links.items():
            if (link_object.get_real_datetime_t() < datetime.now()):
                train_to_remove.add(train_name)
                continue

            if (link_object.datetime_f < datetime.now()
               and not link_object.location_url):
                new_links = Resolver.resolve_mainsite_minutesback(
                    link_object.station_f,
                    link_object.station_t,
                    30
                )
                add_update_newlinks(actual_links, new_links)

        for tr_remove in train_to_remove:
            actual_links.pop(tr_remove, None)
            print('Train removed: ' + tr_remove)

        print("--------- DELAY RESOLVE ---------")
        for train_name, link_object in actual_links.items():
            new_delay = Resolver.resolve_delay(link_object)
            link_object.add_delay(new_delay)

        '''
        print("--------- CHECK PRINT ---------")
        for train_name, link_object in actual_links.items():
            print(link_object)
        '''

        print("--------- DONE - SLEEP ---------")
        print("------ " + str(datetime.now()))
        time.sleep(update_time)

    except Exception as err:
        print("--- ERROR ---")

        error_file = open("logs/error_log.err", "a")

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error_file.write(
            str(datetime.now()) + ": \n" +
            "\t" + str(exc_type) + " " + str(fname) +
            " " + str(exc_tb.tb_lineno) + "\n"
        )
        error_file.close()

        time.sleep(update_time)
