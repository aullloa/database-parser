import argparse
import pandas as pd
from pymongo import MongoClient
import os


parser = argparse.ArgumentParser()

# Flags created to handle different actions and database calls
# action= store => argument required
# action = store_true => no argument required
parser.add_argument("-file", action="store", required=True, help="Input file")
parser.add_argument("-verbose", action="store_true", help="Verbose output")
parser.add_argument("-kevin",action="store_true", help=" Get a report of all \"Work\" that Kevin has done")
parser.add_argument("-rbugs", action="store_true", help="Lists all repeatable bugs")
parser.add_argument("-bbugs", action="store_true", help="Lists all blocker bugs")
parser.add_argument("-RBbugs", action="store_true", help="Lists all repeatable and blocker bugs")
parser.add_argument("-date", action="store_true", help="Lists all reports on build 2/24/2024")

args = parser.parse_args()

try:
    df = pd.read_excel(args.file)

    # This handles creating and accessing correct database based on which file is passed through
    filename = os.path.basename(args.file)
    collection_name = filename.split(".")[0]
    print("Collection Name:", collection_name)

    # Create connection with MongoDB
    client = MongoClient('localhost', 27017)
    database = client["qa_logs"]
    collection = database[collection_name]

    # Inserting data to db
    data = df.to_dict('records')
    collection.insert_many(data)
    print(f"Successfully inserted data into {collection_name} database")

    #  Database Calls
    if args.kevin:
        report = collection.find({"Test Owner": "Kevin Chaja"})
        print(f"Successfully found all of Kevin's entries in {collection_name} database")
        for r in report:
            print(r)
            print("\n")

    if args.verbose:
        print(df.to_string(index=False))

    print("File imported!")
except FileNotFoundError:
    print("File not found")
    exit(1)


