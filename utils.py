import logging
import os
import sys
from datetime import datetime


def convert_name_to_variable(name):
    special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    name = name.replace(" ", "_")
    name = name.lower()
    name = name.translate(special_char_map)
    return name


def convert_date_string_list_to_datetime(string_list, return_first_entry=False):
    date_list = []
    for datetime_str in string_list:
        datetime_object = convert_date_string_to_datetime(datetime_str)
        date_list.append(datetime_object)
    if return_first_entry:
        return date_list[0]
    return date_list


def convert_date_string_to_datetime(string_date):
    datetime_object = datetime.strptime(string_date, '%Y-%m-%d')
    return datetime_object


def check_for_consecutive_dates(date1, date2):
    if abs((date1 - date2).days) == 1:
        return True
    return False


def get_script_folder():
    # determine if application is a script file or frozen exe
    application_path = ""
    if getattr(sys, 'frozen', False):
        logging.info("Ligaman Pro is running as executable")
        # application_path = os.path.dirname(sys.executable)
        application_path = os.path.dirname(__file__)
    elif __file__:
        logging.info("Ligaman Pro is running native Python")
        application_path = os.path.dirname(__file__)
    return application_path


def get_executable_location():
    # determine if application is a script file or frozen exe
    application_path = ""
    if getattr(sys, 'frozen', False):
        logging.info("Ligaman Pro is running as executable")
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        logging.info("Ligaman Pro is running native Python")
        application_path = os.path.dirname(__file__)
    return application_path
