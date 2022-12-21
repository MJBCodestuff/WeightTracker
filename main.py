import os
import re
import sys
from datetime import date
import plotly.express as px

# text
ERRORMSG1 = "Add (a)dd, (d)aily or (w)eekly as argument"
ERRORMSG2 = "No data available"
ERRORMSG3 = "Entry already exists for today, replace? (Y/n)"
ERRORMSG4 = "Exiting..."
FILENAME = "./data.dat"


def addWeight():
    # date formating because it isn't saved as dd.mm.yy
    # instead of ISO 8601 to work with my existing data
    # and make the file more comfortable to read
    today = date.today()
    day = today.day
    if day < 10:
        day = "0" + str(day)
    month = today.month
    if month < 10:
        month = "0" + str(month)
    year = str(today.year)[2:]
    today = f"{day}.{month}.{year}"
    # read existing data
    daily = open(FILENAME).read().split("\n")
    # check if entry for today exists
    replacemode = False
    for line in daily:
        day, _ = line.split(" ")
        if today == day:
            choice = input(ERRORMSG3) or "y"
            # only one entry per day, replace or exit
            if choice.lower() == "y":
                replacemode = True
            else:
                print(ERRORMSG4)
                exit(0)

    weight = input("Weight: ")
    # formating for locale - probably should check how to generalize this
    commaToPoint = re.compile(r",")
    weight = commaToPoint.sub(".", weight)
    if replacemode:
        # save the entire file in memory
        file = open(FILENAME, "r")
        content = file.readlines()
        file.close()
        print(content)
        # change last entry
        content[-1] = f"{today} {weight}"
        # overwrite entire file
        file = open(FILENAME, "w")
        file.write("".join(content))
        file.close()
    else:
        # append new data
        file = open(FILENAME, "a")
        file.write(f"\n{today} {weight}")
        file.close()
    # display with new data
    display("d")
    if date.today().weekday() == 0:
        display("w")


def display(choice="d"):
    # open file, initialize lists
    dataText = open(FILENAME).read()
    dailyDate = []
    dailyWeight = []
    weeklyDate = []
    weeklyWeight = []
    # more date formating ...
    datereg = re.compile(r"(\d\d).(\d\d).(\d\d)")
    dataText = datereg.sub(r"20\3-\2-\1", dataText)
    data = dataText.split("\n")
    for i, line in enumerate(data):
        # skip header
        if i == 0:
            continue
        day, weight = line.split(" ")
        # fooooormating
        day = date.fromisoformat(day)
        weight = float(weight)
        # generate 2x2 lists
        dailyDate.append(day)
        dailyWeight.append(weight)
        if day.weekday() == 0:
            weeklyDate.append(day)
            weeklyWeight.append(weight)
    # display daily weight graph
    if choice == "d":
        try:
            fig = px.line(x=dailyDate, y=dailyWeight, labels={'x': 'Datum', 'y': 'Gewicht'}, markers=True)
            fig.show()
        except ValueError:
            print(ERRORMSG2)
    # display weekly weight graph
    if choice == "w":
        try:
            fig2 = px.line(x=weeklyDate, y=weeklyWeight, labels={'x': 'Datum', 'y': 'Gewicht'}, markers=True)
            fig2.show()
        except ValueError:
            print(ERRORMSG2)


def main():
    # if argument is missing set to trash
    if len(sys.argv) < 2:
        print(ERRORMSG1)
        exit(0)
    choice = sys.argv[1]
    # set working directory to main.py path
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # check for data file, create if not found
    try:
        file = open(FILENAME, "r")
        file.close()
    except FileNotFoundError:
        file = open(FILENAME, "a")
        file.write("Date Weight")
        file.close()
    # choose operation
    if choice == "a":
        addWeight()
    elif choice == "d" or choice == "w":
        display(choice)
    else:
        print(ERRORMSG1)


if __name__ == "__main__":
    main()
