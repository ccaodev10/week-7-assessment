from __future__ import print_function
import requests, json, time
from datetime import date, datetime, timedelta, timezone
from dataclasses import dataclass

@dataclass
class Holiday:
    def __init__(self, name, date):
        self._name = name
        self._date = date

    def get_name(self):
        return self._name
    
    def get_date(self):
        return self._date
    
filename = "Holidays.json"
holiday_list = []
with open(filename) as json_file:
    holiday_file = json.load(json_file)
    for holiday in holiday_file:
        temp_holiday = Holiday(holiday['name'],holiday['date'])
        holiday_list.append(temp_holiday)

print("\nHoliday Management")
print("==================")
print("There are",len(holiday_list),"holidays stored in the system.")

edited = 0 # increments if any changes are made (Added or Removed)
api_key = "de28503000abba2941ecd149deff9c83"
lat = "44.976884" # Minneapolis latitude/longitude
lon = "-93.269999"
weather_dict = {} # master dictionary that stores the current weeks dates and weather to be cross-referenced later
def current_weather(): # current and future API pull
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=minutely,hourly,alerts&appid=%s&units=metric" % (lat, lon, api_key)
    data = requests.get(url).json()
    for day in data['daily']:
        dt = datetime.fromtimestamp( day['dt'], tz=timezone.utc ).strftime('%Y-%m-%d')
        weather_dict.update({dt: day['weather'][0]['description']})
        
def past_weather(): # past 5 days API pull
    for i in range(1,5):
        past_day = int(datetime.strptime(str(date.today() - timedelta(i)),'%Y-%m-%d').timestamp())
        url = "https://api.openweathermap.org/data/2.5/onecall/timemachine?lat=%s&lon=%s&exclude=minutely,hourly,alerts&dt=%s&appid=%s&units=metric" % (lat, lon, past_day, api_key)
        data = requests.get(url).json()
        dt = datetime.fromtimestamp(data['current']['dt'], tz=timezone.utc ).strftime('%Y-%m-%d')
        weather_dict.update({dt: data['current']['weather'][0]['description']})

def validate_date(date_valid):
    try:
        datetime.strptime(date_valid, '%Y-%m-%d')
        return True
    except ValueError:
        print("Incorrect data format, should be YYYY-MM-DD")
        
def option1(): # Add
    print("Add a Holiday")
    print("=============")
    addHoliday = input("Holiday: ")
    date_text = input("Date (yyyy-mm-dd): ")
    if validate_date(date_text) is True:
        print(addHoliday + " (" + date_text + ") has been added to the holiday list.")
        temp_holiday = Holiday(addHoliday,date_text)
        holiday_list.append(temp_holiday)
        global edited
        edited += 1
        
def option2(): # Remove
    print("Remove a Holiday")
    print("================")
    remove_me = input("Holiday name: ")
    def my_decorator(func):
        def wrapper():
            print("Success:",remove_me,"has been removed from the holiday list")
            func()
        return wrapper
    @my_decorator
    def print_delete():
        return
    found = False
    for i, holiday in enumerate(holiday_list):
        if remove_me == holiday.get_name():
            found = True
            del holiday_list[i]
    if found == True:
        print_delete()
        global edited
        edited += 1
    else:
        print("Error:",remove_me,"not found")
        
def option3(): # Save
    print("Save Holiday List")
    print("=================")
    save = input("Are you sure you want to save your changes?: (Y/N): ").upper()
    if save == "Y":
        holiday_list_temp = []
        for holiday in holiday_list:
            holiday_list_temp.append({'name':holiday.get_name(), 'date':holiday.get_date()})
        json_convert = json.dumps(holiday_list_temp, indent = 5)
        k = open(filename,'w')
        k.write(json_convert)
        k.close()
        print("Success: Your changes have been saved.")
    else:
        print("Holiday list file save canceled.")
        
def option4(): # View
    print("View Holidays")
    print("=============")
    year = input("Which year?: ")
    if not year.isnumeric():
        print("Year is not an integer.")
        option4()
    else:
        week = input("Which week? #1-52, leave blank for current week: ")
        if not week.isnumeric() and week != "":
            print("Week is not an integer.")
            option4()
        elif week != "" and (int(week) < 1 or int(week) > 52):
            print("Outside 1-52.")
            option4()
        else:
            ask_weather = ""
            if week == "":
                ask_weather = input("Would you like to see this week's weather? (Y/N): ").upper()
                todaysdate = datetime.today()
                week = (todaysdate.timetuple().tm_yday // 7) + 1
            f = lambda year, week: print("These are the holidays for year "+str(year)+" week #"+str(week)+":\n")
            f(year,week)
            for holiday in holiday_list:
                holiday_object = datetime.strptime(holiday.get_date(),'%Y-%m-%d')
                if holiday_object.year != int(year):
                    continue
                julian = holiday_object.timetuple()
                if julian.tm_yday //7 == int(week)-1:
                    if ask_weather == "Y":
                        print(holiday.get_name() + " (" + holiday.get_date() + ") - " + weather_dict[holiday.get_date()])
                    else:
                        print(holiday.get_name() + " (" + holiday.get_date() + ")")
                    
def option5(): # Exit
    print("Exit")
    print("====")
    if edited == 0: # No edits were made
        bye1 = input("Are you sure you want to exit? [Y/N]: ").upper()
        if bye1 == "Y":
            print("Goodbye!")
            exit()
        elif bye1 == "N":
            print("Canceled. Returning to main menu")
            main_menu()
        else: print ("Not a valid choice. Please choose Y or N." + "\n")
    else : # at least one edit was made
        bye = input("Are you sure you want to leave? Your changes will not be saved. (Y/N): ").upper()
        if bye == "Y":
            print("The program will now exit without saving. Goodbye.")
            exit()
        elif bye == "N":
            print("Canceled. Returning to main menu.")
            main_menu()
        else: print ("Not a valid choice. Please choose Y or N." + "\n")
    option5()
    
def main_menu():
    print()
    print("1. Add a Holiday")
    print("2. Remove a Holiday")
    print("3. Save Holiday List")
    print("4. View Holidays")
    print("5. Exit")
    print()
    option = int(input("Select an option: ")) # non-numbers break the code
    while True:
        if option == 1: # add holiday
            option1()
        elif option == 2: # remove holiday
            option2()
        elif option == 3: # save holiday
            option3()
        elif option == 4: # view holiday
            option4()
        elif option == 5: # exit
            option5()
        else: print ("Invalid selection. Please choose from 1-5")
        main_menu()

current_weather() # gather weather for today's date and the next 7 days
past_weather() # gather the past 5 day's weather and append to weather_dict
main_menu() # begin program