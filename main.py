import os
import re
import sys
import datetime
from datetime import date
import plotly.graph_objects as go

# text
ERRORMSG1 = "Add (a)dd, (d)aily or (w)eekly as argument"
ERRORMSG2 = "No data available"
ERRORMSG3 = "Entry already exists for today, replace? (Y/n)"
ERRORMSG4 = "Exiting..."
ERRORMSG5 = "Input Error, Database has not been touched"
FILENAME = "./data.dat"
GRAPHTITLE = 'Daily and Weekly Weight Progression'
GRAPHX = 'Date'
GRAPHY = 'Weight(kg)'


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
    try:
        float(weight)
    except ValueError:
        print(ERRORMSG5)
        print(ERRORMSG4)
        exit(0)
    if replacemode:
        # save the entire file in memory
        file = open(FILENAME, "r")
        content = file.readlines()
        file.close()
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
    display()


def display():
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
    try:
        fig = go.Figure()
        # daily curve
        fig.add_trace(go.Scatter(x=dailyDate, y=dailyWeight,
                                 name="Daily",
                                 mode='lines+markers',
                                 line=dict(color='firebrick', width=1),
                                 connectgaps=True))
        # weekly curve
        fig.add_trace(go.Scatter(x=weeklyDate, y=weeklyWeight,
                                 name="Weekly",
                                 mode='lines+markers',
                                 line=dict(color='royalblue', width=2),
                                 connectgaps=True))
        # layout
        fig.update_layout(title=GRAPHTITLE,
                          xaxis_title=GRAPHX,
                          yaxis_title=GRAPHY)
        # add minor ticks
        fig.update_yaxes(minor=dict(ticklen=4, tickcolor="black", showgrid=True),
                         minor_ticks="inside")
        # add minor ticks, set range to +-1 day, label only mondays
        fig.update_xaxes(minor=dict(ticklen=4, tickcolor="black", showgrid=True, tickmode="linear"),
                         range=(dailyDate[0] - datetime.timedelta(days=1), dailyDate[-1] + datetime.timedelta(days=1)),
                         tickvals=weeklyDate,
                         minor_ticks="inside")
        fig.show()
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
    elif choice == "d":
        display()
    else:
        print(ERRORMSG1)


if __name__ == "__main__":
    main()
