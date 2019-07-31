#!/usr/bin/env python3

import sys
import os
import json
import datetime

class Person:
    def __init__(self, firstname=None, lastname=None, nickname=None, dob=None, nationality=None):
        self.firstname = firstname
        self.lastname = lastname
        self.dob = dob
        self.nationality = nationality
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

class Event:
    def __init__(self, on_year, on_month=None, on_day=None, on_hour=None, on_minute=None, people_involved=[], location=None, keywords=None, photo_details=None):
        self.on_year = on_year
        self.on_month = on_month
        self.on_day = on_day
        self.on_hour = on_hour
        self.on_minute = on_minute
        self.people_involved = people_involved
        self.location = location
        self.keywords = keywords
        self.photo_details = photo_details

    def __lt__(self, other):
        if self.on_year < other.on_year
        and self.on_month < other.on_month
        and self.on_day < other.on_day
        and self.on_hour < other.on_hour
        and self.on_minute < other.on_minute

class Timeline:
    def __init__(self, list_of_events):
        assert type(list_of_events) is list
        for event in list_of_events:
