#team: Kai Johnson, Songyan Zhao, and Kyosuke Imai

import sys
import csv

"""This method reads the arguments passed from the command line, and :
	if the passed command is 'help', usage.txt is printed
	if the command 'find' is used with an appropriate sub-command (see usage.txt), the dictionary args is filled with appropriate key-value pairs, with the key corresponding to the column the data reside in (starting at column 0), and the value corresponding to the search string the user is looking for in that column
"""
def parse_command_line():
	args = {}
	if len(sys.argv) > 1:          
        #ask for help; the main method will result in this printing usage.txt, and return 1 to indicate no error
		if sys.argv[1] == "help" or sys.argv[1] == "--help" or sys.argv[1] == "-h" :
			for line in open('usage.txt').readlines():
				print(line, end='')
			return 1
            
        #find + sub-command; partitions to appropriate key value in appropriate capitalization and organization
		elif len(sys.argv) > 2 and sys.argv[1] == "find" or sys.argv[1] == "-f" or sys.argv[1] == "--find":
			if sys.argv[2] == "--title" or sys.argv[2] == "-t":
				args[0] = sys.argv[3].lower()
			elif sys.argv[2] == "--year" or sys.argv[2] == "-y":
				args[1] = sys.argv[3].split("-")
			elif sys.argv[2] == "--author" or sys.argv[2] == "-a":
				args[2] = sys.argv[3].lower().split(", ")
				print(args[2])

		return args

"""This method takes a dictionary argument (to allow for later functionality of mutliple commands) and cycles through each row of the data file books.csv
	At each row, it compares its search string against the category it was instructed to search in ("austen" again row[2], which maps to the author) 
	If the row contains the search string in the appropriate position, the row is printed (in a format constructed with method get_string())
"""
def find(commands):
	with open('books.csv', newline="\n") as csvbooks:
		reader = csv.reader(csvbooks, delimiter=",", quotechar="\"") 
		for row in reader:
			for key in commands.keys():
				value = commands.get(key) #reduces confounding method calls; improves readability
				if key == 0 and value in row[key].lower(): #searching for a title
					print(get_string(row))
				elif key == 1 and value[0] <= row[key] and value[1] >= row[key]: #searching for a year
					print(get_string(row))
				elif key == 2 and len(value) > 0: #searching for (an) author(s)
					for author in value:
						if author in row[key].lower():
							print(get_string(row)) 

"""This method returns a string of the author, title, and publication date given an input of an array."""
def get_string(books_row):
    return books_row[0] + ", published: " + books_row[1] + ", written by: " + books_row[2].split("(")[0]

"""This method prints the content of usage.txt (with information on how to format the command line argument correctly) """
def show_help():
    for line in open('usage.txt').readlines():
        print(line)

"""Execution of the program
	if neither find (with an appropriate sub-command) nor help was called, print an error message
"""
args = parse_command_line()
if args and args != 1:
	find(args)
elif args != 1:
	print("error! invalid command. type 'help', '--help', or '-h' for description of commands supported by this CLI.")
