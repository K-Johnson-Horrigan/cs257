#team: Kai Johnson, Songyan Zhao, and Kyosuke Imai
#revised by: Kai Johnson, Songyan Zhao, and Kyosuke Imai

import sys
import csv 
import argparse
from collections import defaultdict
import re

"""This program provides a command line interface for searching for books with certain authors, publication years, and titles in the data file "books.csv" and then printing the search result.  For description of the CLI tags offered by this program, see the "usage.txt" in this folder.  To run this program, run "books.py"."""

def main():
	"""Reads the command line, prints usage.txt if necessary, prints a  context-specific string error message if author/year input is invalid, else prints the rows satisfying the user's search commands"""
	command_line_arguments = get_command_line_arguments()

	if need_help(command_line_arguments): 
		print_usage_txt()
	elif invalid_year_format(command_line_arguments):
		print_invalid_year_format_error_message()
	else: 
		dictionary_of_search_commands = turn_arguments_into_dictionary(command_line_arguments)

		dictionary_of_search_results = search_csv_into_dictionary(dictionary_of_search_commands)

		print_search_results(dictionary_of_search_commands, dictionary_of_search_results)

def get_command_line_arguments():
	"""Return parsed arguments made using argparse."""
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--help", "-h", action="store_true")
	parser.add_argument("--author", "-a", help = 'Enter the authors name, e.g. --author "Austen, morrison, tolstoy". Support mutiple search.')
	parser.add_argument("--title", "-t",  type =str, help = 'Enter the title name, e.g. -t "Crime and PUNishment".')
	parser.add_argument("--year", "-y", help = 'Enter the year or year range, e.g. --year "1980-1991".')
	return parser.parse_args()	

def need_help(command_line_arguments):
	"""This method returns true if '-h, --help, help' is entered in the command line argument or if there is no argument entered. Otherwise, returns false."""
	has_argument = command_line_arguments.title or command_line_arguments.author or command_line_arguments.year
	if command_line_arguments.help or not has_argument: 
		return True
	return False

def print_usage_txt():
	"""This method prints the content of usage.txt (with examples demonstrating how to format the command line arguments correctly)."""
	for line in open('usage.txt').readlines():
		print(line, end='')
	print()

def invalid_year_format(command_line_arguments):
	"""Checks the input year format, if invalid returns true."""
	year_input_string = command_line_arguments.year
	if year_input_string and re.search(r"^\d+(-){1}\d+((,){1}(\s){1}\d+(-){1}\d+)*$", year_input_string) is None:
		return True
	return False

def print_invalid_year_format_error_message():
	"""Prints to the console a description of what the year format should be."""
	print("Sorry, the years entered don't seem to fit the format \"A-B\" (with years constructed using numerals 0-9) with additional year pairs added within the quotations with a comma and a space, in the format \"A-B, C-D\". Enter command -h/--help for more information.", file=sys.stderr)

def turn_arguments_into_dictionary(command_line_arguments):
	"""Returns a dictionary with keys as search categories and values holding the search string populated from the user's command line arguments"""
	csv_title_index = 0; csv_year_index = 1; csv_author_index = 2
	dictionary_of_search_commands = {}
	if command_line_arguments.title:
		dictionary_of_search_commands[csv_title_index] = [command_line_arguments.title]
	if command_line_arguments.year:
		dictionary_of_search_commands[csv_year_index] = command_line_arguments.year.split(", ")
	if command_line_arguments.author:
		dictionary_of_search_commands[csv_author_index] = command_line_arguments.author.split(", ")
	return dictionary_of_search_commands

def search_csv_into_dictionary(dictionary_of_search_commands):
	"""Returns a dictionary with key search strings and value csv rows that satisfy the search command, from data file books.csv."""
	dictionary_of_search_results = defaultdict(list)
	with open('books.csv', newline="\n") as csvbooks:
			reader = csv.reader(csvbooks, delimiter=",", quotechar="\"")
			for csv_row in reader:
				for search_category in dictionary_of_search_commands:
					for search_string in dictionary_of_search_commands[search_category]:
						if search_string_is_in_row(search_category, search_string, csv_row):
							dictionary_of_search_results[search_string].append(csv_row)
	return dictionary_of_search_results

def search_string_is_in_row(search_category, search_string, csv_row):
	"""Returns boolean representation of whether a given search string was found in its given category in a given row."""
	csv_title_index = 0; csv_year_index = 1; csv_author_index = 2
	if search_category == csv_title_index: 
		return title_is_in_row(search_string, csv_row[csv_title_index])
	elif search_category == csv_year_index:
		return row_year_is_in_bounds(search_string, csv_row[csv_year_index])	
	elif search_category == csv_author_index:
		return author_is_in_row(search_string, csv_row[csv_author_index])
	return False

def title_is_in_row(title_search_string, title_row):
	"""Returns true if the target title in the passed row."""
	return title_search_string.lower() in title_row.lower()

def row_year_is_in_bounds(years_search_string, year_row):
	"""Returns true if the year in the passed row is in the passed year bound."""
	list_years_search_string = years_search_string.split("-")

	year_in_low_to_high_bounds = (list_years_search_string[0] <= year_row and year_row <= list_years_search_string[1])
	year_in_high_to_low_bounds =  (list_years_search_string[1] <= year_row and year_row <= list_years_search_string[0])

	return year_in_low_to_high_bounds or year_in_high_to_low_bounds

def author_is_in_row(author_search_string, author_row):
	"""Returns true if the author search string is found at the author position in the row."""
	return author_search_string.lower() in clean_row_author_info(author_row.lower())

def clean_row_author_info(row_author_info):
	"""Returns a string of author info stripped of parentheses or numericals"""
	clean_row_author_info = ""
	for i in range(len(row_author_info)):
		undesirable_characters = "()-"
		if row_author_info[i].isnumeric() or row_author_info[i] in undesirable_characters:
			continue
		clean_row_author_info += row_author_info[i]
	return clean_row_author_info

def print_search_results(dictionary_of_search_commands, dictionary_of_search_results):
	"""Prints to the console the results of the user's search under headings for each different search string."""
	for search_category in dictionary_of_search_commands:
		for search_string in dictionary_of_search_commands.get(search_category):
			header_string = get_header_string(search_category, search_string)	
			print(header_string)
			if dictionary_of_search_results.get(search_string):
				for book_csv_row in dictionary_of_search_results.get(search_string):
					book_printable_string = get_printable_string(book_csv_row)
					print(book_printable_string, end="\n\n")
			else:
				print("Nothing was found!")

def get_printable_string(csv_row):
	"""Returns a string format (to be printed to console) for row passed to method."""
	csv_title_index = 0; csv_year_index = 1; csv_author_index = 2
	printable_string = "Title: " + csv_row[csv_title_index]
	printable_string += "\nYear Published: " + csv_row[csv_year_index]
	printable_string += "\nAuthor: " + clean_row_author_info(csv_row[csv_author_index])
	return(printable_string)

def get_header_string(search_category, search_string):
	"""Returns personalized heading text depending on the passed search category."""
	header_string = ""
	csv_title_index = 0; csv_year_index = 1; csv_author_index = 2
	if search_category == csv_title_index:
		header_string = "\n\nResults books with titles containing: "
	elif search_category == csv_year_index:
		header_string = "\n\nResults for books published in the years: "
	elif search_category == csv_author_index:
		header_string = "\n\nResults for books written by: "
	return header_string + search_string

"""The main method is called and the method is executed."""
main()
