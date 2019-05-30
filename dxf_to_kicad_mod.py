# !/usr/bin/python3
import collections
import sys
import csv
import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import fileinput

def plot_poly(polygon):
    """
    This functions plots the polygon created using the CAD model

    Parameters
    ----------
    polygon : list of list
        polygon is a list of polygons lists. Each polygon list contains the coordinate to form that polygon

    Returns
    -------
    void
        Plots the polygons givens in the list

    """
    # Plot each polygon in the list
    for points in polygon:
        plt.plot(*zip(*(points + points[:1])), marker='o')

    # Can choose a different scaling if un-comment lines below
    # automin, automax = plt.xlim()
    # plt.xlim(automin - 0.5, automax + 0.5)
    # automin, automax = plt.ylim()
    # plt.ylim(automin - 0.5, automax + 0.5)
    plt.axis('scaled')

    # Displays the plots of the polygons
    plt.show()


def flip_column(column_name):
    """
    This function flips coordinate columns

    Parameters
    ----------
    column_name : str
        column_name is a string defining which column is currently being observed

    Returns
    -------
    str
        Returns the column not under observation. If column_name is "End Pkt", it would return "Start Pkt"

    """
    if column_name == 'Start Pkt':
        return 'End Pkt'
    else:
        return 'Start Pkt'

def parse_coordinates(shape):
    """
    This function takes in a shape, which is a list of coordinates and prepared them for implementation

    Parameters
    ----------
    shape : list of list of coordinates (strings)
        shape is a list that contains a list of coordinates. Each coordinates represents a corner of a shape

    Returns
    -------
    list of lists
        Returned shape in a parsed matter

    """

    # Create two place-holder lists
    x_coordinate = []
    y_coordinate = []

    # for each coordinate in shape, it is being parsed/modified for the correct form for later use
    for coordinate in shape:
        # Take out paranthesis and commas
        shape_list = coordinate.replace('(', '').replace(')', '')
        shape_split = shape_list.split(",")

        # Append each coordinate x and y values to the appropriate place-holder list
        x_coordinate.append(float(shape_split[0]))
        y_coordinate.append(float(shape_split[1]))

    # combine coordinates into the appropriate x,y format for kicad_mod
    coordinates = []
    for x, y in zip(x_coordinate, y_coordinate):
        coordinates.append((x, y))

    return coordinates
# -------------------------------------------- START MAIN ------------------------------------------------------------

# Reads and input
input_file_name = sys.argv[1]

output_file_name = 'out_' + input_file_name

# Takes in a outline of the dxf kicad_mod as input
input = open(input_file_name, "r") #opens file with name of "test.txt"

# Create a pattern objeect for all the lines associated with the kicad_mod outline footprint
pattern = re.compile(r"fp_line")

# Create a list that will hold all the lines that have "fp_line" phrase in them
fp_lines = []
# Counter veriable
linenum = 0

# Variable to define the start line of "fp_line"
start_line = 0
# line_check will be able to determine the start line value
line_check = True
# Create a panda dataphrame to hold all the "fp_line"
df = pd.DataFrame(columns=['Line Number', 'Start Coordinate', 'End Coordinate',
                           'Start Pkt', 'End Pkt'])

# Goes through and appends all the lines that have "fp_line" to the fp_lines list
for line in input:
    linenum += 1
    if pattern.search(line) != None:  # If pattern search finds a match,
            fp_lines.append((linenum, line.rstrip('\n')))
            if line_check:
                line_check = False
                start_line = linenum

# Create a polygon list
polygon = []

# Evaluate each "fp_line" and enter it into the dataframe. Phrase through and assign each
# variable to the right variable in the dataframe
for line in fp_lines:
    start = line[1].find('start')
    end = line[1].find(')')
    if start != -1 and end != -1:
        start_coordinate = line[1][start:end].replace("start ", "")
    start1 = line[1][end:].find('end')
    end1 = line[1][end+1:].find(')')
    if start1 != -1 and end1 != -1:
        end_coordinate = line[1][start1+end:end1+end+1].replace("end ", "")

    start_x = start_coordinate.split()[0]
    start_y = start_coordinate.split()[1]
    end_x = end_coordinate.split()[0]
    end_y = end_coordinate.split()[1]

    start_pkt = '(' + start_coordinate.split()[0] + ',' + start_coordinate.split()[1] + ')'
    end_pkt = '(' + end_coordinate.split()[0] + ',' + end_coordinate.split()[1] + ')'

    polygon.extend((start_pkt, end_pkt))
    df = df.append({'Line Number': line[0], 'Start Coordinate': start_coordinate,'End Coordinate': end_coordinate,
                    'Start Pkt': start_pkt, 'End Pkt': end_pkt}, ignore_index=True)

# get the total length of the dataframe
df_length = len(df.index)

# Somtimes there are duplicate coordinates. This functions drops those rows
df = df.drop_duplicates(subset=['Start Pkt', 'End Pkt'], keep='first',)

# Initialize all lists and variables
total_shape = []
line_index = []
row_index = []
index_count = 0

# Will exit loop once dataframe is empty signaling that all shapes are grouped
while not df.empty:
    shape = []

    # Initializes the index count for each shape
    index_count = 0
    row_index_val = 0
    column_choice = 'Start Pkt'
    row_index = []

    # reset index after dropped frames & eliminate the index column it generates after re-indexing
    df = df.reset_index()
    df = df.drop(columns=['index'])

    # Takes the head of the dataframe and generates a new shape
    shape.append(df.head(1).values[index_count][3])  # saves the coordinates for the shape
    last_value = df.head(1).values[index_count][4]  # saves last value to see when shape is complete
    line_index.append(df.head(1).values[index_count][0])  # saves the line in the kicad_mod
    row_index.append(0)  # saves the row index associated with the dataframe

    # Delete row in dataframe for no repeated coordinates
    df = df.drop(0)

    # Ensures that the last value in the shape coordinates doesn't match the last value to see when shape is complete
    while shape[-1] != last_value:
        # Starts search for the coordinate in Start Pkt Column
        column_choice = 'Start Pkt'

        # Re-indexes again as head of dataframe was dropped
        df = df.reset_index()
        df = df.drop(columns=['index'])

        # checks to see if the column currently under search has the next coordinate, if not flips
        if not df[column_choice].isin(shape).any(axis=None):
            if column_choice == 'Start Pkt':
                column_choice = 'End Pkt'
            elif column_choice == 'End Pkt':
                column_choice == 'Start Pkt'
            else:
                raise Exception('NO MATCHING COORDINATE WAS FOUND. MAJOR FAILURE!!')

        # Ensures that the new coordinate found is doesn't have associated coordinate that is the end coordinate
        for idx, val in df[column_choice].isin(shape).iteritems():
            if val:
                row_index_val = idx
                if df[flip_column(column_choice)].values[idx] == last_value:
                    break

        # Appends th row of the found coordinate to the row_index list
        row_index.append(row_index_val)
        index_count += 1

        # Depending on the column of choice the opposite coordinate would be added
        if column_choice == 'Start Pkt':
            shape.append(df.iloc[(row_index[-1])][4])
            comp_val = df.iloc[(row_index[-1])][3]
        elif column_choice == 'End Pkt':
            shape.append(df.iloc[(row_index[-1])][3])
            comp_val = df.iloc[(row_index[-1])][4]


        # Delete row in dataframe for no repeated coordinates
        df = df.drop(row_index[-1])

    # Once a shape is complete the shape list is added to final total_shape list
    total_shape.append(shape)

# Create a list of properly parsed shapes' coordinates
parse_total_shape = []

for s in total_shape:
    parse_total_shape.append(parse_coordinates(s))

total_fp_poly = []
fp_poly = ''

# Generate and store the lines necessary for the kicad_mod to create the shape
for poly in total_shape:
    fp_poly = ' (fp_poly (pts '
    for coor in poly:
        fp_poly +=  '(xy ' + coor.replace("(", "").replace(")", "") + ')'

    fp_poly += ') (layer F.Cu) (width 0.15))'
    total_fp_poly.append(fp_poly.replace(",", " "))

# Creates a copy of the input files and saves it under the name defined in output_file_name
shutil.copyfile(input_file_name, output_file_name)

# output = open(output_file_name, "r") #opens file with name of "test.txt"
line_count = 0

# open the output file and reads all the lines
with open(output_file_name, 'r') as reader:
    # Note: readlines doesn't trim the line endings
    ki_cad_mod_file = reader.readlines()

phrase = "fp_line"

# opens the output file and writes over the fp_lines and adds all the fp_poly lines after word based on the start line
with open(output_file_name, 'w') as writer:
    #
    for line in ki_cad_mod_file:
        line_count += 1
        if phrase in line:
            continue

        writer.write(line)
        if line_count == (start_line-1):
            for fp_poly_line in total_fp_poly:
                writer.write(fp_poly_line + '\n')

# prints new kicad_mod file
with open(output_file_name, 'r') as reader:
    print(reader.read())

# plots the polygon you should see on the kicad_mod if opened with kicad footprint feature
plot_poly(parse_total_shape)
