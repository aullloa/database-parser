# Alfredo Ulloa
# COMP 467
# Project 2
# Script to parse data from a csv file and import to a db.
# Uses argparse to perform different functions with data.

import argparse
import random
import sys
import pandas as pd
from pymongo import MongoClient, errors
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
parser.add_argument("--date",type=str, action="store", help="Lists all reports on given build date")
parser.add_argument("--debug", action="store_true", help="Debug mode")

args = parser.parse_args()

all_data = []
results = []
data_tracker = set()

def baking_the_cake(data, flag_type, filename="baking_the_cake.csv"):
    output_messages = (
        "Adding sweet delicious cream...",
        "Mixing the flour with the eggs...",
        "Preheating the oven to 467°F...",
        "Frosting the edges...",
        "Adding sugar, spice, and everything nice...",
        "Sprinkling the strawberries on top..."
    )
    message = random.choice(output_messages)
    print(message.upper())

    with open(filename, "a", newline="") as file:
        file.write("\n")
        file.write("$" * 50 + "\n")
        file.write(f"{flag_type.upper()}\n")
        file.write(f"# {message.upper()}\n")
        file.write("$" * 50 + "\n")
        data.to_csv(file, index=False)

try:
    # Connecting to db
    client = MongoClient('localhost', 27017)
    database = client["qa_logs"]

    # Available databases
    if args.file:
        df = pd.read_excel(args.file)

        # This handles creating and accessing correct database
        # based on which file is passed through
        filename = os.path.basename(args.file)
        collection_name = filename.split(".")[0]
        collection = database[collection_name]

        # text casing is lowered
        for col in df.columns:
            df[col] = df[col].astype(str).str.lower()

        # Standardize the date formats
        if "Build #" in df.columns:
            df["Build #"] = pd.to_datetime(df["Build #"], errors="coerce")
            df["Build #"] = df["Build #"].dt.strftime("%m/%d/%Y")

        # Insert data to collection
        data = df.to_dict('records')
        collection.insert_many(data)
        print(f"Successfully inserted data into {collection_name}")
        sys.exit(0)

    # Checking for duplicates based on the given columns
    list_of_tables = database.list_collection_names()
    for table in database.list_collection_names():
        collection = database[table]
        for row in collection.find({}):
            key = (row["Test Case"], row["Test Owner"], row["Actual Result"])
            if key not in data_tracker:
                data_tracker.add(key)
                all_data.append(row)

    df = pd.DataFrame(all_data)

    #  Database Calls
    if args.verbose:
        print(df.to_string(index=False))

    if args.user:
        username = args.user.lower().strip()
        report = df[df["Test Owner"] == username]
        print(f"Successfully found all of {username}'s entries in database")
        baking_the_cake(report, f"{username} Report")
        try:
            export_file = open(f"{username}-report.csv", "wb")
        except FileNotFoundError:
            print("File not found")
            sys.exit(0)
        report = report.drop(columns=["_id"])
        report.to_csv(export_file)
        print(f"Successfully exported to {username}-work.csv")

    if args.repeat:
        results = [
            r for r in all_data
            if any(option in r["Repeatable?"] for option in ("yes", "y"))]
        report = pd.DataFrame(results)
        baking_the_cake(report, "Repeatable Report")

    if args.blocker:
        results = [
            r for r in all_data
            if any(option in r["Blocker?"] for option in ("yes", "y"))]
        report = pd.DataFrame(results)
        baking_the_cake(report, "Blocker Report")

    if args.rb:
        results = [
            r for r in all_data
            if any(option in r["Repeatable?"] for option in ("yes", "y"))
               and any(option in r["Blocker?"] for option in ("yes", "y"))]
        report = pd.DataFrame(results)
        baking_the_cake(report, "Repeatable and Blocker Report")

    if args.date:
        try:
            date = pd.to_datetime(args.date).strftime("%m/%d/%Y")
        except ValueError:
            print("Invalid date. Make sure date is in the format MM/DD/YYYY")
            sys.exit(1)
        results = [
            r for r in all_data
            if r["Build #"] == date]
        report = pd.DataFrame(results)
        baking_the_cake(report, f"{date} Report")

except FileNotFoundError:
    print("File not found")
    exit(1)
except errors.ConnectionFailure:
    print("Connection failed with database(Is the database running?)")
    exit(1)