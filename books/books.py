#team: Kai Johnson, Songyan Zhao, and Kyosuke Imai

import sys
import csv 
import argparse

"""Global variable that makes the program more readable, as each variable corresponds to the column in the csv that holds the category of information"""
title_category = 0
year_category = 1
author_category = 2

"""Reads the command line, prints usage.txt if necessary, or prints the rows containing the search strings if not"""
def main():
	arguments = get_command_line_arguments()
	useable_arguments = turn_arguments_into_lists(arguments)
	if need_help(useable_arguments, arguments):
		print_usagetxt()
	else:
		search_csv_and_print_match(useable_arguments[0], useable_arguments[1])

"""Parse arguments and return parsed arguments using argparse
"""
def get_command_line_arguments():
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("-h", "--help", action="store_true")
	parser.add_argument("--author", "-a", help = 'Enter the authors name, e.g. --author "Austen, morrison, tolstoy". Support mutiple search.')
	parser.add_argument("--title", "-t",  type =str, help = 'Enter the title name, e.g. -t "Crime and PUNishment".')
	parser.add_argument("--year", "-y", help = 'Enter the year or year range, e.g. --year "1980-1991".')
	return parser.parse_args()

"""Create the searching string and searching category from the user input in the shell"""
def turn_arguments_into_lists(arguments):
	search_string_list = []
	search_category_list = []
	if arguments.title:
		search_string_list.append(arguments.title.lower())
		search_category_list.append(title_category)
	if arguments.year:
		search_string_list.append(arguments.year.split("-"))
		search_category_list.append(year_category)
	if arguments.author:
		search_string_list.append(arguments.author.lower().split(", "))
		search_category_list.append(author_category)
	return [search_string_list, search_category_list]

"""This method reads the arguments of the user and if either nothing was entered or a help flag was entered returns false
"""
def need_help(usable_args, parsed_args):
	if len(usable_args)==0 or parsed_args.help==True:
		return True
	return False

"""This method prints the content of usage.txt (with information on how to format the command line arguments correctly) """
def print_usagetxt():
	for line in open('usage.txt').readlines():
		print(line, end='')
	print()

"""This method takes the arguments of the list of search strings and the list of search categories and then goes through every line of books.csv, and if any of the search strings match to their appropriate category in the row, prints the row.
"""
def search_csv_and_print_match(search_string_list, search_category_list):
	with open('books.csv', newline="\n") as csvbooks:
		reader = csv.reader(csvbooks, delimiter=",", quotechar="\"")
		for row in reader:
			for i in range(0, len(search_string_list)):
				search_string = search_string_list[i]
				search_category = search_category_list[i]
				if search_string_is_in_row(search_string, search_category, row):
					print(get_string(row))
		
"""This method takes in the searching string, the searching category, and the target row, to check if the row contains the desired information."""
def search_string_is_in_row(search_string, search_category, row):
	if search_category == title_category: 
		return title_is_in_row(search_string, row[title_category])
	elif search_category == year_category:
		return row_year_is_in_bounds(search_string, row[year_category])	
	elif search_category == author_category:
		return author_is_in_row(search_string, row[author_category])
	return False

"""This method returns if the target title in the row or not."""
def title_is_in_row(title_search_string, title_row):
	return title_search_string in title_row.lower()

"""This method checks if the year in this row is in the year bound."""
def row_year_is_in_bounds(years_search_string, year_row):
	return (years_search_string[0] <= year_row and year_row <= years_search_string[1]) or (years_search_string[1] <= year_row and year_row <= years_search_string[0])

"""This method checks if any of the passed authors wrote the book in the current row"""
def author_is_in_row(authors_search_string, authors_row):
	for author in authors_search_string: 
		if author in authors_row.lower():
			return True
	return False

"""This method returns a string of the author, title, and publication date given an input of an array."""
def get_string(books_row):
    return books_row[title_category] + ", published: " + books_row[year_category] + ", written by: " + books_row[author_category]


"""The main method is called and the method is executed."""
main()
