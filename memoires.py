#!/usr/bin/env python3

import sys
import os
import json
import datetime
import functools
import math

TIMELINE_CHAR_LENGTH = 100
DAYS_IN_MONTH = 31
DAYS_IN_YEAR = 365
MONTHS_IN_YEAR = 12

class Person:
    def __init__(self, firstname=None, lastname=None, nickname=None, dob=None, nationality=None):
        self.firstname = firstname
        self.lastname = lastname
        self.dob = dob
        self.nationality = nationality
        self.birth_year = int(dob[:4])
        if firstname == None and lastname == None and nickname == None:
            raise Exception("Person must have a name")

        # Each person must be identifyable by a name, the nickname should always be filled
        if nickname == None:
            if firstname == None:
                self.nickname = lastname
            else:
                self.nickname = firstname

class AssociatedPerson(Person):
    pass

class MemoirOwner(Person):
    pass

class Location:
    def __init__(self, street=None, suburb=None, city=None, state=None, country=None, region=None, lat=None, lon=None):
        self.street = street
        self.suburb = suburb
        self.city = city
        self.state = state
        self.country = country
        self.region = region
        self.lat = lat
        self.lon = lon

    def reproject(from_crs, to_crs):
        print("Nothing setup for this yet")

@functools.total_ordering
class Event:
    def __init__(self, story, on_year, on_month=None, on_day=None, on_hour=None, on_minute=None, people_involved=None, location=None, keywords=None, photo_details=None):
        self.story = story
        self.on_year = on_year

        if on_month is None:
            self.on_month = 1
            self.on_month_unknown = True
        else:
            self.on_month = on_month
            self.on_month_unknown = False

        if on_day is None:
            self.on_day = 1
            self.on_day_unknown = True
        else:
            self.on_day = on_day
            self.on_day_unknown = False

        if on_hour is None:
            self.on_hour = 0
            self.on_hour_unknown = True
        else:
            self.on_hour = on_hour
            self.on_hour_unknown = False

        if on_minute is None:
            self.on_minute = 0
            self.on_minute_unknown = True
        else:
            self.on_minute = on_minute
            self.on_minute_unknown = False

        self.people_involved = people_involved
        self.location = location
        self.keywords = keywords
        self.photo_details = photo_details

    def datetuple(self):
        return (self.on_year, self.on_month, self.on_day, self.on_hour, self.on_minute)

    def datetime(self):
        return datetime.datetime(year = self.on_year,
                                 month = self.on_month,
                                 day = self.on_day,
                                 hour = self.on_hour,
                                 minute = self.on_minute)

    def timeline_summary(self):
        return "{} {}".format(self.datetime().date(), self.story)

    ## Overrides for sorting (less than/equal than)
    def __lt__(self, other):
        return ((self.on_year, self.on_month, self.on_day, self.on_minute) <
                (other.on_year, other.on_month, other.on_day, other.on_minute))

    def __eq__(self, other):
        return ((self.on_year, self.on_month, self.on_day, self.on_minute) ==
                (other.on_year, other.on_month, other.on_day, other.on_minute))

class Timeline:
    def __init__(self, list_of_events, owner):
        assert type(list_of_events) is list
        self.list_of_events = list_of_events
        self.list_of_events.sort()
        self.start_date = list_of_events[0].datetime()
        self.end_date = list_of_events[-1].datetime()
        self.owner = owner

        self.date_summary = {}
        for event in list_of_events:
            yearmonth_id = "{:04}{:02}".format(event.datetuple()[0], event.datetuple()[1]) # yyyymm
            year_id = "{:04}".format(event.datetuple()[0]) # yyyy

            # Make a dictionary item for each yyyymm to keep a count per month
            if yearmonth_id in self.date_summary:
                self.date_summary[yearmonth_id] += 1
            else:
                self.date_summary[yearmonth_id] = 1

            # Do the same for years
            if year_id in self.date_summary:
                self.date_summary[year_id] += 1
            else:
                self.date_summary[year_id] = 1

    def print_timeline(self):
        start_string = "[start] {}".format(self.start_date)
        end_string = "[end] {}".format(self.end_date)

        day_delta = (self.end_date - self.start_date).days
        month_delta = day_delta / DAYS_IN_MONTH
        year_delta = day_delta / DAYS_IN_YEAR

        print("{} days, {} months, {} years".format(day_delta,
                                                    round(month_delta,2),
                                                    round(year_delta),2))
        if (day_delta / TIMELINE_CHAR_LENGTH) < 1:
            step = ("Days", math.ceil(TIMELINE_CHAR_LENGTH / day_delta))
        elif (month_delta / TIMELINE_CHAR_LENGTH) < 1:
            step = ("Months", math.ceil(TIMELINE_CHAR_LENGTH / month_delta))
        else:
            step = ("Years", math.ceil(TIMELINE_CHAR_LENGTH / year_delta))

        #print("Scale: {} | Step: {}".format(step[0], str(round(step[1],2))))


        #print(start_string)
        #print("|")
        #[print("=", end="") for i in range(TIMELINE_CHAR_LENGTH)]
        #print()
        #[print(" ", end="") for i in range(TIMELINE_CHAR_LENGTH-1)]
        #print("|")
        #[print(" ", end="") for i in range(TIMELINE_CHAR_LENGTH-len(end_string))]
        #print(end_string)
        #print()

        #for idx, event in enumerate(self.list_of_events):
            #print("[{:2}] {}".format(idx, event.timeline_summary()))
        print()
        print("      |JAN| |FEB| |MAR| |APR| |MAY| |JUN| |JUL| |AUG| |SEP| |OCT| |NOV| |DEC|")
        print("-----------------------------------------------------------------------------")
        for year in range(self.owner.birth_year, datetime.datetime.now().year+1):
            print(str(year) + ": ", end='')
            for month in range(1, MONTHS_IN_YEAR + 1): # Offset months by 1 for realism
                combined_tuple = "{:04}{:02}".format(year, month)
                if combined_tuple in self.date_summary:
                    month_count = self.date_summary[combined_tuple]
                else:
                    month_count = 0
                print("|{0:3}|".format(month_count), end=' ')
            if str(year) in self.date_summary:
                print("({:02})".format(self.date_summary[str(year)]), end=' ')
                for count in range(self.date_summary[str(year)]):
                    print("*", end='')
            print()

    def print_yearlist(self):
        print(self.start_date)
        print(self.end_date)


event_list = []
event_list.append(Event("something happened here when", 1995, 4, 1, 12, 3))
event_list.append(Event("something happened here when", 1995, 4, 1, 12, 3))
event_list.append(Event("something else happened here", 1996, 12, 4))
event_list.append(Event("something else happened here", 1996, 12, 5))
event_list.append(Event("something else happened here", 1996, 4, 6))
event_list.append(Event("something else happened here", 1996, 2, 6))
event_list.append(Event("something else happened here", 1996, 12, 6))
event_list.append(Event("nothing happened", 1998, 2, 3, 16, 1))

memoire_owner = Person(firstname='john',
                       lastname='smith',
                       nickname=None,
                       dob='19950101',
                       nationality='empty')

timeline1 = Timeline(event_list, memoire_owner)
#print(timeline1.owner.birth_year)
timeline1.print_timeline()
timeline1.print_yearlist()
