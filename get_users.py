#!/usr/bin/env python3

"""Get Bitrix Users

This program retrieves users from Bitrix24 and processes the data.

Usage:
    get_users.py (-c <FILE> | --config <FILE>)
    get_users.py (-h | --help)
    get_users.py --version

Options:
    -h --help   Show this screen.
    --version   Show version.
    -c --config Configuration file.

"""

# -*- coding: utf-8 -*-
# For documentation
from docopt import docopt

# For logging
# https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
# https://www.loggly.com/ultimate-guide/python-logging-basics/
import logging
import logging.handlers
import os
# Retrieve the name of current function
import inspect

# JSON handling
import json

# CSV and JSON file operations and printing
import modules.file_ops as file_ops

# CSV handling
import csv

# Time stamps to files
from datetime import datetime

# For creating requests to GitHub API
import requests

# For parsing configurations
from modules.conf_parser import ConfParser

def get_user_json(conf: ConfParser = None):
    
    logging.info("Retriving users from Bitrix24")
    response = requests.get(conf.get_users_webhook_url())
    file_ops.write_json_dump(response.json(), "bitrix24_all_user_data", conf.get_output_path())
    
    return response.json()

def get_deparment_json(conf: ConfParser = None):
    
    logging.info("Retriving department from Bitrix24")
    response = requests.get(conf.get_department_webhook_url())

    file_ops.write_json_dump(response.json(), "bitrix24_department_data", conf.get_output_path())
    
    return response.json()

def add_parent_departments_recursively(
        dep_json: list = None,
        dep_cur: dict = None,
        dep_hierarchy: list = None):
    """Add parent departments recursively.
    
    Paremeters
    ----------
    dep_json : dict
        A JSON which was retrieved from Bitrix24. The JSON contains departments.
    dep_cur : dict
        The department which is being checked currently.
    dep_hierarcy_str : str
        
    """

    # The root will not have PARENT. 
    if "PARENT" in dep_cur:
        for tmp_dep in dep_json["result"]:
            if int(dep_cur["PARENT"]) == int(tmp_dep["ID"]):
                dep_hierarchy[0] = '{} -> {}'.format(tmp_dep["NAME"], dep_hierarchy[0])
                add_parent_departments_recursively(dep_json, tmp_dep, dep_hierarchy)

def combine_users_and_departments(conf: ConfParser = None):

    users_json = get_user_json(conf)
    department_json = get_deparment_json(conf)

    org = dict()
    for department in department_json["result"]:
        org[department["ID"]] = {
                "NAME": department["NAME"],
                "ID": department["ID"],
                "head": {},
                "employees": {}}
        # Every department doesn't have UF_HEAD or PARENT
        if "UF_HEAD" in department:
            org[department["ID"]]["UF_HEAD"] = department["UF_HEAD"]
        if "PARENT" in department:
            org[department["ID"]]["PARENT"] = department["PARENT"]
            parent_hierarchy = [department["NAME"]]
            #parent_hierarchy.append(department["NAME"])
            add_parent_departments_recursively(department_json, department, parent_hierarchy) 
            org[department["ID"]]["parent_hierarchy"] = parent_hierarchy[0]
        
        for user in users_json["result"]:
            if user["ACTIVE"]:
                for uf_dep in user["UF_DEPARTMENT"]:
                    # If user belongs to the department, check more.
                    
                    # If the user is the head of the deparment,
                    # add to head. Otherwise add to employees.
                    if "UF_HEAD" in department and user["ID"] == department["UF_HEAD"]:
                        org[department["ID"]]["head"] = {
                                "ID": user["ID"],
                                "EMAIL": user["EMAIL"],
                                "NAME": user["NAME"],
                                "LAST_NAME": user["LAST_NAME"]}

                    if int(uf_dep) == int(department["ID"]):
                        # The departements are not necessarily in an order that user would be added
                        # as department head before checking if user is part of department.
                        # Somehow in Bitrix24 one can be department head, but user_json information
                        # doesn't show it.
                        if "UF_HEAD" in department and user["ID"] == department["UF_HEAD"]:
                            pass
                        else:
                            org[department["ID"]]["employees"][user["ID"]] = {
                                    "ID": user["ID"],
                                    "EMAIL": user["EMAIL"],
                                    "NAME": user["NAME"],
                                    "LAST_NAME": user["LAST_NAME"],
                                    "USER_TYPE": user["USER_TYPE"]}


    file_ops.write_json_dump(org, "bitrix24_org", conf.get_output_path())
    return org

def main():
    arguments = docopt(__doc__, version='Bitrix24 Get Users 0.1')
    config = ConfParser()
    config.load_ini_conf(arguments["--config"])

    # Create log file
    log_to_file(config, "bitrix24_get_users")

    # Print loaded configuration
    logging.info("Loaded configuration:\n" + config.get_conf_str())

    logging.info("Combining users with departments")
    org = combine_users_and_departments(config)
    
    file_ops.write_csv_org(org, "org", config.get_output_path())

    #file_ops.write_csv_nodes(nodes, "vms", config.get_output_path())

# Example:
# https://realpython.com/python-logging/
def log_to_file(config: ConfParser = None, log_id: str = None):
    log_path = config.get_log_path()
    log_name = log_path + log_id + "_" + \
            datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"

    # Probably some import initializes the logging already,
    # but logging needs to be initialized this way to get the
    # output to certain file.
    # https://stackoverflow.com/a/46098711
    logging.root.handlers = []
    logging.basicConfig(level=config.get_logging_level(), \
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_name),
                logging.StreamHandler()
            ]
    )

if __name__ == '__main__':
    main()
