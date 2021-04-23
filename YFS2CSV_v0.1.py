#!/usr/bin/env python

__author__ = "Decaff_42"
__contact__ = "decaff_42 on ysfhq.com"
__copyright__ = "2017 by Decaff_42"
__license__ = "GNU GPLv3"
__date__ = "24 July 2017"
__version__ = "0.1"

"""
PURPOSE:
The purpose of this tool is to take each sortie of an aircraft in the .yfs
file and extract the raw data into a csv file in order to make flight testing
an aircraft more accurate. 

HOW TO USE:
Press F5 or Click Run and follow the on-screen prompts
"""

# Load Modules
import os
import csv
import time


def Break():
    print("---------------------------------------------------------")


def PrintHeader():
    """Prints the preamble of the software into the command window."""
    print("YFS2CSV Converter")
    print("Version {}".format(__version__))
    print("By {}".format(__author__))
    print("Copyright (c) {}".format(__copyright__))
    print("Licensed under {}".format(__license__))
    Break()
    print(("Refer to the Reference Document for License information, \n"
           "instructions and for any questions about the output of \n"
           "this program. Further questions may be addressed to \n"
           "decaff_42 via a Private Message on YSFlight Headquarters."))
    Break()         


def CreateFileStructure():
    """Detect file structure of the Current Working Directory and
    if there are missing folders, create them"""
    
    cwd = os.getcwd()
    folder_names = ["Input YFS Files", "Output CSV Files",
                    "Documentation"]
    for name in folder_names:
        dirpath = os.path.join(cwd, name)
        if not os.path.exists(dirpath):
            if name is not folder_names[-1]:
                os.makedirs(dirpath)
                print("Created {} Folder".format(name))
            else:
                print("Documentation Folder Missing.")


def DetectYFS():
    """Find YFS files in the Input YFS Folder and report names for selection"""
    cwd = os.getcwd()
    dirpath = os.path.join(cwd, "Input YFS Files")
    files = os.listdir(dirpath)
    
    YFS_files = []
    for name in files:
        if name.endswith(".yfs"):
            YFS_files.append(name)
    
    if len(YFS_files) < 1:
        print(("No YFS files were found. \n"
               "Please place your YFS files in the 'Input YFS Files' folder."))
        return False    
    else:
        print("Select a File to Load")
        for ind, file in enumerate(YFS_files):
            print("({}) {}".format(ind, file))

        selected = -1
        while selected < 0:
            selected = Validate(len(YFS_files))

    Break()        
    return YFS_files[selected]


def Validate(max_num):
    """Checks the input from the user to make sure it is a valid option given
    the number of files to select from.
    """
    user_input = input("Enter File Number Here:")

    try:
        user_input = int(user_input)
        if user_input >= 0 and user_input <= max_num:
            return user_input
        else:
            print("Provided number is not a valid option.")
            return -1
    except:
        print("Please enter the number to the left of the file name")
        return -1


def ExtractAirplane(fname):
    """Extract each sortie recorded in the .yfs file.
    Ask the user to select the sortie to parse to csv file
    """
    if fname is False:
        print("Stopping Program")
        return False

    print("Extracting data from {}".format(fname))

    raw_yfs = []
    fpath = os.path.join(os.getcwd(), "Input YFS Files", fname)
    with open(fpath) as input_file:
        for line in input_file:
            raw_yfs.append(line[:-1])

    print("Raw Data Extracted... \nLooking for sorties to convert.")

    flight = []
    sorties = []
    flights = {}
    record = False
    for ind, line in enumerate(raw_yfs):
        if line.startswith("AIRPLANE") and record is False:
            record = True
        elif (line.startswith("AIRPLANE") \
              or line.startswith("BULRECOR")) \
              and record is True:
            record = False
            
            temp = sortie(flight,ind)
            sorties.append(temp.gen_sortie_name())
            flights["{}".format(len(sorties)-1)] = temp
            
            flight = []
            flight.append(line)

        if record is True:
            flight.append(line)

    if len(sorties) < 1:
        print("No Sorties Detected")
        return False
    else:
        print("Select Sortie to convert to CSV.")
        for ind, s in enumerate(sorties):
            print("({}) {}".format(ind,s))
            
        selected = -1
        while selected < 0:
            selected = Validate(len(sorties))

        print("Parsing Sortie Data.")
        data = flights[str(selected)].parse()
        return data

           
def WriteCSV(data):
    """Write list of lists data to csv and add headers"""
    Break()
    headers = ["Time","X-Pos","Y-Pos","Z-Pos", "Compass Heading",
               "Pitch Angle","Bank Angle","G","Flight State",
               "Variable Geometry Wing","Air Brake","Landing Gear",
               "Flaps","Brakes","Smoke","Vapor Trail","Misc","Strength",
               "Throttle","Elevator","Aileron","Rudder","Trim",
               "Thrust Vector","Reverse Thrust","Bomb Bay","Turrets"]
    units = ["second","meter","meter","meter", "radians",
             "radians","radians","N/A","N/A",
             "N/A","N/A","N/A",
             "N/A","N/A","N/A","N/A","N/A","N/A",
             "N/A","N/A","N/A","N/A","N/A",
             "N/A","N/A","N/A","N/A"]

    output = []
    output.append(headers)
    output.append(units)
    
    for line in data:
        output.append(line)

    print("Please enter a name for the output csv file.")
    fname = input("CSV Name:")
    if fname == "":
        fname = "YFS2CSV_{}_{}".format(time.strftime('%d-%B-%Y'),
                                       time.strftime('%H.%M.%S'))
        
    if fname.endswith(".csv") is False:
        fname = fname + ".csv"

    fpath = os.path.join(os.getcwd(),"Output CSV Files",fname)
    with open(fpath,"w") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerows(output)

    print("Data Written to File: {}".format(fname))
    
    
        

"""Class written to help extract data"""
class sortie():
    def __init__(self,raw,raw_start):
        """Initialize Class Instance with raw data defining aircraft.
        Note: Not all of this data is used in YFS2CSV v0.1. Future releases
        may be expanded to utilize some of this data.
        """
        self.raw = raw
        self.aircraft_name = ""
        self.username = ""
        self.start_position = ""
        self.parsed_data = []
        self.raw_start = raw_start
        self.raw_data = []
        self.NUMRECOR = 0
        self.start = 0
        self.sortie_name = ""

        self.extract_data_from_header()
        

    def extract_data_from_header(self):
        """Takes the header block of the aircraft's raw data and assigns
        values for important variables.
        """
        for ind,row in enumerate(self.raw):
            if row.startswith("AIRPLANE"):
                self.aircraft_name = row.split()[1]
            elif row.startswith("STARTPOS"):
                self.start_position = row[12:]
            elif row.startswith("AIRPCMND INITFUEL"):
                self.start_fuel = int(row.split()[-1][:-1])
            elif row.startswith("AIRSPEED"):
                self.start_speed = float(row.split()[-1][:-3])
            elif row.startswith("THROTTLE"):
                self.start_throttle = float(row.split()[-1])
            elif row.startswith("NUMRECOR"):
                self.NUMRECOR = int(row.split()[1])
                self.start = ind
                break
        

    def gen_sortie_name(self):
        """Generate the sortie name"""
        if self.username == "":
            self.sortie_name = self.aircraft_name
        else:
            self.sortie_name = self.aircraft_name + self.username
        return self.sortie_name
    
        
    def parse(self):
        """Parses Flight Data into a list of lists."""
        self.data = self.raw[self.start+1:]
        self.parse_data = []
        row_num = 0
        slices = 0
        while slices < self.NUMRECOR:           
            line = self.data[row_num].split()
            line.extend(self.data[row_num + 1].split())
            line.extend(self.data[row_num + 2].split())
            line.extend(self.data[row_num + 3].split())
            
            self.parse_data.append(line)
            row_num += 4
            slices += 1

        return self.parse_data
            


""" Run the code"""
def RunYFS2CSV():
    """Run through the process"""
    PrintHeader()
    CreateFileStructure()
    WriteCSV(ExtractAirplane(DetectYFS()))

    print("\n\n")
    Break()

    print("Run Again? 0 = Yes / 1 = No")
    if int(input("")) == 0:
        print("\n\n")
        RunYFS2CSV()
    


# Call Function to Run the Code
RunYFS2CSV()

