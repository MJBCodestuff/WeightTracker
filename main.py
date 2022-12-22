import os
import re
import sys
import datetime
from datetime import date
import plotly.graph_objects as go

# text
ERRORMSG1 = "Add (a)dd, (d)isplay or (t)able as argument"
ERRORMSG2 = "No data available"
ERRORMSG3 = "Entry already exists for today, replace? (Y/n)"
ERRORMSG4 = "Exiting..."
ERRORMSG5 = "Input Error, Database has not been touched"
FILENAME = "./data.dat"
GRAPHTITLE = 'Daily and Weekly Weight Progression'
GRAPHX = 'Date'
GRAPHY = 'Weight(kg)'
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def add_weight():
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
    comma_to_point = re.compile(r",")
    weight = comma_to_point.sub(".", weight)
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


def read_data():
    # open file, initialize lists
    data_text = open(FILENAME).read()
    daily_date = []
    daily_weight = []
    # more date formating ...
    datereg = re.compile(r"(\d\d).(\d\d).(\d\d)")
    data_text = datereg.sub(r"20\3-\2-\1", data_text)
    data = data_text.split("\n")
    for i, line in enumerate(data):
        # skip header
        if i == 0:
            continue
        day, weight = line.split(" ")
        # fooooormating
        day = date.fromisoformat(day)
        weight = float(weight)
        # generate 2 lists
        daily_date.append(day)
        daily_weight.append(weight)
    return daily_date, daily_weight


def display():
    # get monday values for a fixed weekly comparison
    weekly_date = []
    weekly_weight = []
    daily_date, daily_weight, = read_data()
    for i, day in enumerate(daily_date):
        if day.weekday() == 0:
            weekly_date.append(day)
            weekly_weight.append(daily_weight[i])
    # display daily weight graph
    try:
        fig = go.Figure()
        # daily curve
        fig.add_trace(go.Scatter(x=daily_date, y=daily_weight,
                                 name="Daily",
                                 mode='lines+markers',
                                 line=dict(color='RGB(0,206,209)', width=1),
                                 connectgaps=True))
        # weekly curve
        fig.add_trace(go.Scatter(x=weekly_date, y=weekly_weight,
                                 name="Weekly",
                                 mode='lines',
                                 line=dict(color='RGB(238,48,167)', width=2),
                                 connectgaps=True))
        # line to show average developement from start to today
        fig.add_trace(go.Scatter(x=[daily_date[0], daily_date[-1]], y=[daily_weight[0], daily_weight[-1]],
                                 name="Average",
                                 mode="lines",
                                 line=dict(color="RGB(110,110,110)", width=1),
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
                         range=(daily_date[0] - datetime.timedelta(days=1),
                                daily_date[-1] + datetime.timedelta(days=1)),
                         tickvals=weekly_date,
                         minor_ticks="inside")
        fig.show()
    except ValueError:
        print(ERRORMSG2)


def overview_table():
    daily_date, daily_weight = read_data()
    collection = [[] for x in range(7)]
    weightloss_by_weekday = []
    # split every delta up into the corresponding weekday
    for i in range(1, len(daily_date), 1):
        collection[daily_date[i].weekday()].append(daily_weight[i] - daily_weight[i - 1])
    # get the average for each weekday
    for i, day in enumerate(collection):
        weightloss_by_weekday.append(round(sum(day) / len(day) * 1000, 2))
        # formatting
        if weightloss_by_weekday[i] >= 0:
            weightloss_by_weekday[i] = "+" + '{:06.2f}'.format(weightloss_by_weekday[i])
        else:
            weightloss_by_weekday[i] = '{:07.2f}'.format(weightloss_by_weekday[i])
    # calculate lost weight and averages
    loss = (daily_weight[-1] - daily_weight[0]) * 1000
    daily_avg = loss / len(daily_weight)
    weekly_avg = daily_avg * 7
    # format and print weekday stats
    for i, day in enumerate(weightloss_by_weekday):
        part1 = f"  {WEEKDAYS[i]} "
        for j in range(len(part1), 16):
            part1 += " "
        print(f"{part1} {day}g")
    # format and print other averages
    print(f"  Daily Average  {'{:.7s}'.format('{:07.2f}'.format(daily_avg))}g")
    print(f"  Weekly Average {'{:.7s}'.format('{:07.2f}'.format(weekly_avg))}g")
    print(f"Weightloss Total {'{:.7s}'.format('{:07.2f}'.format(loss))}g")


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
        add_weight()
    elif choice == "d":
        display()
    elif choice == "t":
        overview_table()
    else:
        print(ERRORMSG1)


if __name__ == "__main__":
    main()
