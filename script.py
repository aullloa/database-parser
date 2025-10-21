import argparse
import sys
import csv
import pandas as pd
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
data_tracker = set()

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
    for table in database.list_collection_names():
        collection = database[table]
        for row in collection.find({}):
            key = (row["Test Owner"], row["Test Case"], row["Actual Result"])
            if key not in data_tracker:
                data_tracker.add(key)
                all_data.append(row)

        #DEBUG: to check data has no duplicates
        with open("no_dupes.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames = all_data[0].keys())
            writer.writeheader()
            writer.writerows(all_data)
        # END DEBUG

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


