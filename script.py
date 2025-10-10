import argparse
import pandas as pd
from pymongo import MongoClient

#Create connection with MongoDB
client = MongoClient('localhost', 27017)
database = client["qa_logs"]
collection = database["EGSpring"]

parser = argparse.ArgumentParser()

# Flags created to handle different actions and database calls
parser.add_argument("-file", action="store", required=True, help="Input file")
parser.add_argument("-verbose", action="store_true", help="Verbose output")
parser.add_argument("-kevin", action="store", help=" Get a reportt of all \"Work\" that Kevin has done")
parser.add_argument("-rbugs", help="Lists all repeatable bugs")
parser.add_argument("-bbugs", help="Lists all blocker bugs")
parser.add_argument("-RBbugs", help="Lists all repeatable and blocker bugs")
parser.add_argument("-date", action="store", help="Lists all reports on build 2/24/2024")

args = parser.parse_args()

try:
    df = pd.read_excel(args.file)
    data = df.to_dict('records')
    collection.insert_many(data)
    print("Successfully inserted data into database")
    if args.verbose:
        print(df.to_string(index=False))
    print("File imported!")
except FileNotFoundError:
    print("File not found")
    exit(1)

