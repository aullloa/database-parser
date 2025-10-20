import argparse
import sys

import pandas as pd
from pandas import ExcelWriter
from pymongo import MongoClient
import os


parser = argparse.ArgumentParser()

# Flags created to handle different actions and database calls
# action= store => argument required
# action = store_true => no argument required
parser.add_argument("--file", action="store", required=False, help="Input file to create database")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("--user",action="store", help=" Get a report of a specified user")
parser.add_argument("-rbugs", action="store_true", help="Lists all repeatable bugs")
parser.add_argument("-bbugs", action="store_true", help="Lists all blocker bugs")
parser.add_argument("-RBbugs", action="store_true", help="Lists all repeatable and blocker bugs")
parser.add_argument("-date", action="store_true", help="Lists all reports on build 2/24/2024")

args = parser.parse_args()

all_data = []

try:

    # Connecting to db
    client = MongoClient('localhost', 27017)
    database = client["qa_logs"]

    # Available databases
    if args.file:
        df = pd.read_excel(args.file)

        # This handles creating and accessing correct database based on which file is passed through
        filename = os.path.basename(args.file)
        collection_name = filename.split(".")[0]
        collection = database[collection_name]

        # Insert data to collection
        data = df.to_dict('records')
        collection.insert_many(data)
        print(f"Successfully inserted data into {collection_name} collection")
        sys.exit(0)


    list_of_tables = database.list_collection_names();
    for table in list_of_tables:
        collection = database[table]
        print("Contents:")
        for row in collection.find({}):
            all_data.append(row)
        print(all_data)

    #  Database Calls
    # Need to modify to take in a string as an input
    if args.user:
        report = collection.find({"Test Owner": "Kevin Chaja"})
        print(f"Successfully found all of Kevin's entries in {collection_name} database")
        try:
            export_file = open("Chaja's work.xlsx", "wb")
        except FileNotFoundError:
            print("File not found")
        for r in report:
            r.to_excel(export_file)

    if args.verbose:
        print(df.to_string(index=False))

except FileNotFoundError:
    print("File not found")
    exit(1)


