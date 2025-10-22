import argparse
import sys
import pandas as pd
from pymongo import MongoClient
import os


parser = argparse.ArgumentParser()

# Flags created to handle different actions and database calls
# action= store => argument required
# action = store_true => no argument required
parser.add_argument("--file", action="store", required=False, help="Input file to create database from contents")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("--user",action="store", help="Get a report of a specified user")
parser.add_argument("--repeat", action="store_true", help="Lists all repeatable bugs")
parser.add_argument("--blocker", action="store_true", help="Lists all blocker bugs")
parser.add_argument("--rb", action="store_true", help="Lists all repeatable and blocker bugs")
parser.add_argument("--date", action="store", help="Lists all reports on given build date")
parser.add_argument("--debug", action="store_true", help="Debug mode")

args = parser.parse_args()

all_data = []
data_tracker = set()
flag_query = []

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

    # Need to add further checks to catch incorrect data  e.g. incorrect data format, inconsistent data in wrong columns
    # Date: need to convert to readable data
    list_of_tables = database.list_collection_names()
    for table in database.list_collection_names():
        collection = database[table]
        for row in collection.find({}):
            key = (row["Test Owner"], row["Test Case"], row["Actual Result"])
            if key not in data_tracker:
                data_tracker.add(key)
                all_data.append(row)

    df = pd.DataFrame(all_data)
    #DEBUG: to check data has no duplicates
    if args.debug:
        df.to_excel("no_dupes.xlsx", index=False)
        print("no_dupes.xlsx created")
    # END DEBUG

    #  Database Calls
    # Need to modify to take in a string as an input
    if args.verbose:
        print(df.to_string(index=False))

    if args.user:
        username = args.user
        report = df[df["Test Owner"] == username]
        print(f"Successfully found all of {username}'s entries in database")
        try:
            export_file = open(f"{username}-work.xlsx", "wb")
        except FileNotFoundError:
            print("File not found")
        report.to_excel(export_file)
        print(f"Successfully exported to {username}-work.xlsx")

    if args.repeat:
        for r in all_data:
            if r["Repeatable?"] == "Yes":
                print(r)
                #flag_query.append(r)
            #print(flag_query)

    if args.blocker:
        for r in all_data:
            if r["Blocker?"] == "Yes":
                print(r)

    if args.rb:
        for r in all_data:
            if r["Repeatable?"] == "Yes" and r["Blocker?"] == "Yes":
                print(r)

    if args.date:
        for r in all_data:
            if r["Date?"] == args.date:
                print(r)

except FileNotFoundError:
    print("File not found")
    exit(1)


