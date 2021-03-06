from bs4 import BeautifulSoup
import requests
from datetime import time

# this class represents a flight which consists of associated flights, an ID, an airline, a destination,
# a status (delayed, on time, arrived), a time (arrival or departure), the terminal, and gate
class flight():

  # the fields in flight
  associates = []
  flightId = ""
  airline = ""
  destination = ""
  status = ""
  time = ""
  terminal = ""
  gate = ""

  # method to create a flight
  def __init__(self, airline_code, airline_name, flight_number, destination, status, schedule_time, update_time, terminal, gate):
    self.flightId = "" + airline_code + " " + flight_number
    self.airline = airline_name
    self.destination = destination
    self.status = status
    self.time = update_time
    self.terminal = terminal
    self.gate = gate

  # how each flight is output. In the future, each associated flight will also be listed
  def __str__(self):
    return self.flightId + " " + self.destination + " " + self.time

  # if the flights are associated
  # E.g. a DAL flight that also is listed as KLM. Same time and same destination.
  def addAssociate(self, flight):
    self.associates.append(flight.flightId)

  # function to determine if two flights are equal
  # def equals(self, fl):
    
  #   if self.time == fl.time:
  #     if self.destination == fl.destination:
  #       if self.terminal == fl.terminal:
  #         if self.gate == fl.gate:
  #           return True
  #   return False

  # def __eq__(self, other):
  #   """Overrides the default implementation"""
  #   if isinstance(other, flight):
  #     if self.time == fl.time:
  #       if self.destination == fl.destination:
  #             return True
  #   return False

# this class stores all of the flight objects
class flight_list():

  flights = [flight]

  # the only function that I needed to explicityly define is how a flight
  # should be added to the list. The function checks to see if the flight
  # already exists, and if it does it is added to the associates
  def add(self, fl=flight):
    equal = False
    for x in self.flights:
      equal_flights = False
      if x.time == fl.time:
        if x.destination == fl.destination:
              equal_flights = True
      if equal_flights:
        x.addAssociate(fl)
        equal = True
    if not equal:
      self.flights.append(fl)

# function to convert the time from a string to a string in 24hr format
# that I can work with   
def convertTime(time):
  hrs = time[0:(time.index(":"))]
  mins = time[(time.index(":") + 1) : (time.index(":") + 3)]
  if ((time[len(time) - 2] == 'P') & (hrs != "12")):
    hrs = int(hrs) + 12
  return "" + str(hrs) + ":" + str(mins)

# a funciton to convert time back to 12 hour time so that I can display the time
# with an 'AM' or 'PM'
def convertBack(time):
  start = time
  end = start + 1
  if (start > 12):
    start_str = str(start - 12) + ":00 PM"
  elif (start < 12):
    start_str = str(start) + ":00 AM"
  else:
    start_str = str(start) + ":00 PM"
  
  if (end > 12):
    end_str = str(end - 12) + ":00 PM"
  elif (end < 12):
    end_str = str(end) + ":00 AM"
  elif (end == 24):
    end_str = str(end - 12) + ":00 AM"
  else:
    end_str = str(end) + ":00 PM"

  return start_str + " and " + end_str

# the url's containing data for arrivals and departures
url_arrivals = 'https://tracker.flightview.com/FVAccess2/tools/fids/fidsDefault.asp?accCustId=FVWebFids&fidsId=20001&fidsInit=arrivals&fidsApt=RDU&fidsFilterAl=&fidsFilterDepap='
url_departures = 'https://tracker.flightview.com/FVAccess2/tools/fids/fidsDefault.asp?accCustId=FVWebFids&fidsId=20001&fidsInit=departures&fidsApt=RDU&fidsFilterAl=&fidsFilterDepap='

# the header to make the request. Ensuring the server that this is only for personal use
headers = {'UserAgent': 'Brian Alonso (alonsobrian2@gmail.com) – Personal Use'}

# requesting data from the two url's
response = requests.get(url_arrivals,headers)
response2 = requests.get(url_departures,headers)

# creating beautiful soup objects to parse the data
soup = BeautifulSoup(response.text, 'html.parser')
soup2 = BeautifulSoup(response2.text, 'html.parser')

# retrieving the relevant data
body = soup.find(class_='data')
body2 = soup2.find(class_='data')

# writing data to a file until I understand beautiful soup better
f = open("data.txt","w+")
f.write(body.get_text())
f.write(body2.get_text())
f.close

f = open("data.txt", "r")
data = []
if f.mode == 'r': # check to make sure that the file was opened
    
    fl = f.readlines() # readlines to read the individual lines into a list

    # checking for blank lines
    for x in fl:
      if not x.isspace():
        if x.endswith('\n'):
          index = x.index("\n")
          string = x[0:index]
        else:
          string = x
        data.append(string)

    # creating an array of flights
    flights = flight_list()
    while (len(data) > 5):
      airline_code = data.pop(0)[10:12]
      airline_name = data.pop(0)
      flight_number = data.pop(0)
      destination = data.pop(0)
      status = data.pop(0)
      schedule_time = convertTime(data.pop(0))
      # if there isnt an update time, use the schedule time
      update_time = convertTime(data.pop(0)) if not (data[0][0:1].isalpha()) else schedule_time
      terminal = ""
      gate = ""
      # retriving terminal and gate from the data
      if len(data) > 0:
        if (len(data[0]) >= 4) & (data[0][0:4] == "Term"):
          location = data.pop(0)
          terminal = location[0:6]
          gate = location[9:len(location)]
        elif (len(data[0]) < 15) & (len(data[0]) > 0):
          data.pop(0)
      # generating a flight
      fl = flight(airline_code,airline_name,flight_number,destination,status,schedule_time,update_time,terminal,gate)
      flights.add(fl)

    # using a loop to initialize the array to 0 for practice
    frequency = []
    for x in range (0,24):
      frequency.append(0)
    # compute the volume of air traffic
    # v01 is computed in hour intervals
    # v02 computed in 15 minute blocks?
    for (i, fl) in enumerate(flights.flights):
      time = str(fl.time)
      if len(time) > 0:
        hr = int(time[0:time.index(":")])
        frequency[hr] = frequency[hr] + 1
    print("\n" + str(max(frequency)) + " flights between " + convertBack(frequency.index(max(frequency))) + "\n")

f.close # closing file to prevent resource leak