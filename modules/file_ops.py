#!/usr/bin/env python3

# For logging into file
import logging

# Retrieve the name of current function
import inspect

# JSON handling
import json

# CSV handling
import csv

# Time stamps to files
from datetime import datetime

def open_json(file_name: str = None):
    """Opens a JSON file.
    Parameters
    ----------
    str
        To be opened file with path.
    """

    if not file_name:
        logging.error("Func: {} no file_name given.".format(inspect.stack()[0][3]))
        return

    logging.debug("Opening JSON file: " + file_name)
    json_file = ""
    try:
        with open(file_name, 'r') as f:
            json_file = json.load(f)
    except (IOError, IsADirectoryError) as e:
        logging.error(e)

    return json_file

def get_json_dump(json_obj):
    """Function for creating prettyPrint JSON."""

    if not json_obj:
        logging.error("Func: {} no JSON obj given.".format(inspect.stack()[0][3]))
        return

    return json.dumps(json_obj, indent=4, ensure_ascii=False)

def print_json_dump(json_obj: list = None):
    """Function mainly for test console prints"""

    if not json_obj:
        logging.error("Func: {} no JSON obj given.".format(inspect.stack()[0][3]))
        return
    
    print(json.dumps(json_obj, indent=4, ensure_ascii=False))

def write_json_dump(json_obj: list = None,
        file_name: str = None,
        output_path: str = None):
    """Writes JSON dump to given folder.

    Parameters
    ----------


    Returns
    -------
    str
        Output dir + filename
    """

    if not json_obj:
        logging.error("Func: {} no JSON obj given.".format(inspect.stack()[0][3]))
        return
    if not file_name:
        logging.warning("Func: {} no file_name given.".format(inspect.stack()[0][3]))
        file_name = "no_name_given"
    if not output_path:
        logging.error("Func: {} no output_path given.".format(inspect.stack()[0][3]))
        return

    file_out = output_path + file_name + "_" + \
            datetime.now().strftime("%Y%m%d-%H%M%S") + \
            ".json"
    logging.info("Writing JSON: " + file_out)
    with open(file_out, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4, ensure_ascii=False)

    return file_out

def write_csv_org(org_dict: dict = None,
        file_name: str = None,
        output_path: str = None):
   
    if not org_dict:
        logging.error("Func: {} no org_dict given.".format(inspect.stack()[0][3]))
        return
    if not file_name:
        logging.warning("Func: {} no file_name given.".format(inspect.stack()[0][3]))
        file_name = "no_name_given"
    if not output_path:
        logging.error("Func: {} no output_path given.".format(inspect.stack()[0][3]))
        return

    file_out = output_path + file_name + "_" + \
            datetime.now().strftime("%Y%m%d-%H%M%S") + \
            ".csv"
    
    logging.info("Writing CSV of organisation: " + file_out)
    
    with open(file_out, mode='w') as outfile:
        org_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        org_writer.writerow([
            'Company',
            'Head',
            'Employees',
            'Email'])

        for dep_val in org_dict.values():
            # If the in organisation root, meaning ID == 1
            if dep_val["NAME"] == org_dict.get("1", None).get("NAME"):
                parent_hierarchy = org_dict.get("1", None).get("NAME")
            else:
                parent_hierarchy = dep_val["parent_hierarchy"]
 
            # Write department head if there's one. 
            if dep_val["head"]:
                head = dep_val["head"]["NAME"] + " " + dep_val["head"]["LAST_NAME"]
                head_email = dep_val["head"]["EMAIL"]
                org_writer.writerow([
                    parent_hierarchy,
                    head,
                    "",
                    head_email])
           
            if not dep_val["head"] and dep_val["employees"]:
                for employee in dep_val["employees"].values():
                    name = employee["NAME"] + " " + employee["LAST_NAME"]
                    org_writer.writerow([
                        parent_hierarchy,
                        "",
                        name,
                        employee["EMAIL"]
                        ])

            # Write employees on their own rows.
            elif dep_val["employees"]:
                for employee in dep_val["employees"].values():
                    name = employee["NAME"] + " " + employee["LAST_NAME"]
                    org_writer.writerow([
                        "",
                        "",
                        name,
                        employee["EMAIL"]
                        ])
    
    # Return the file path str
    return file_out

def convert_list_to_str(list_obj: list = None, separator: str = None):
    if not list_obj:
        logging.error("Func: {} no list_obj given.".format(inspect.stack()[0][3]))
        return
    if not separator:
        logging.error("Func: {} no separator given.".format(inspect.stack()[0][3]))
        return
    
    tmp_str = ""
    for item in list_obj:
        if tmp_str:
            tmp_str += separator
        if item is None:
            tmp_str += "None"
        else:
            tmp_str += item

    return tmp_str
