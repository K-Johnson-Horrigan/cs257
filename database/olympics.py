#author: Kai Johnson

import argparse
import psycopg2
from config import database, user, password

"""Constructs a CLI enabling users to use 3 commands to view information for the database described in olympics.sql, as well as supporting a help command."""

def main():
    """Reads the command line, prints usage.txt if necessary, retrieves the  cursor depiction of the user's search results and then prints them to the console."""
    command_line_arguments = get_command_line_arguments()
    if need_help(command_line_arguments):
        print_usage_txt()
    else:
        search_results = get_search_results(command_line_arguments)
        print_search_results(search_results, command_line_arguments)

def get_command_line_arguments():
	"""Return parsed command line arguments made using argparse."""
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--help", "-h", action="store_true")
	parser.add_argument("--listAthletesFromNOC", "-lan", help = 'Lists all the athletes from an NOC specified by its abbreviation.')
	parser.add_argument("--listGoldMedalsOfNOCs", "-lmn", action="store_true")
	parser.add_argument("--listTopAthletesOfSport", "-las", help = 'Lists the athletes of the specified sport in descending order of their gold medal count')
	return parser.parse_args()

def need_help(command_line_arguments):
	"""This method returns true if '-h, --help, help' is entered in the command line argument or if there is no argument entered. Otherwise, returns false."""
	has_argument = command_line_arguments.listAthletesFromNOC or command_line_arguments.listGoldMedalsOfNOCs or command_line_arguments.listTopAthletesOfSport
	if command_line_arguments.help or not has_argument:
		return True
	return False

def print_usage_txt():
	"""This method prints the content of usage.txt (with examples demonstrating how to format the command line arguments correctly)."""
	for line in open('usage.txt').readlines():
		print(line, end="")
	print()

def get_search_results(command_line_arguments):
    """Connects to the database, retrieves the argument-specific SQL query and  search-string, and retrieves then returns the cursor result of the query"""
    database_connection = get_connection()
    if database_connection:
        cursor_parameters = get_cursor_parameters(command_line_arguments)
        return get_cursor(database_connection, cursor_parameters)

def get_connection():
    """Attempts to connect to a database with parameters passed from config.py, returns connection or prints error and returns null string if connection failed."""
    connection = ""
    try:
        connection = psycopg2.connect(database=database, user=user, password=password)
    except Exception as e:
        print(e)
    return connection

def get_cursor_parameters(command_line_arguments):
    """Depending on the command line arguments, returns a list with position 0 as the SQL query and position 1 as the search string if it exists."""
    if command_line_arguments.listAthletesFromNOC:
        return get_lan_cursor_parameters(command_line_arguments.listAthletesFromNOC)
    elif command_line_arguments.listGoldMedalsOfNOCs:
        return get_lmn_cursor_parameters()
    elif command_line_arguments.listTopAthletesOfSport:
        return get_las_cursor_parameters(command_line_arguments.listTopAthletesOfSport)
    return None

def get_lan_cursor_parameters(noc_name):
    """Returns list with position 0 as a SQL query to find all athletes from a specified NOC and position 1 as the search string description of the specified NOC's abbreviation."""
    search_string = noc_name
    query = '''SELECT DISTINCT
        athletes.full_name
    FROM
        athletes,
        linking_table,
        national_olympic_committees
    WHERE
        linking_table.national_olympic_committee_id = national_olympic_committees.id AND
        national_olympic_committees.abbreviation = %s AND
        linking_table.athlete_id = athletes.id
    ORDER BY
        athletes.full_name'''
    return [query, search_string]

def get_lmn_cursor_parameters():
    """Returns list with position 0 as the SQL query to find the gold medal counts of all the NOCs in the database and display them in descending order of gold medals."""
    query = '''SELECT
      national_olympic_committees.country,
      COUNT(linking_table.medal_id) AS gold_medals
    FROM
      national_olympic_committees
    LEFT JOIN
      linking_table
    ON
      linking_table.national_olympic_committee_id = national_olympic_committees.id
      AND
      linking_table.medal_id = '2'
    GROUP BY
      national_olympic_committees.country
    ORDER BY
      gold_medals DESC'''
    return [query]

def get_las_cursor_parameters(sport_name):
    """Returns list with position 0 as the SQL query to find the gold medal counts of all athletes who have participated in a specified sport, sorted by number of gold medals, and position 1 as the search string describing the specified sport."""
    search_string = sport_name
    query = '''SELECT
      athletes.full_name,
      COUNT(*) AS gold_medals
    FROM
      sports,
      athletes,
      linking_table,
      medals
    WHERE
      linking_table.sport_id = sports.id AND
      sports.sport = %s AND
      linking_table.medal_id = medals.id AND
      medals.medal = 'Gold' AND
      linking_table.athlete_id = athletes.id
    GROUP BY
      athletes.full_name
    ORDER BY
      gold_medals DESC'''
    return [query, search_string]

def get_cursor(database_connection, cursor_parameters):
    """Execute the passed SQL query with search string string if one exists and returns the resulting cursor object."""
    try:
        cursor = database_connection.cursor()
        if len(cursor_parameters) == 2:
            cursor.execute(cursor_parameters[0], (cursor_parameters[1],))
        elif len(cursor_parameters) == 1:
            cursor.execute(cursor_parameters[0])
        return cursor
    except Exception as e:
        print(e)
        return None

def print_search_results(search_results, command_line_arguments):
    """Prints the search results of the user's search to the console."""
    header = get_header_text(command_line_arguments)
    print(header)
    for row in search_results:
        formated_row = get_formated_row(row)
        print(formated_row)

def get_header_text(command_line_arguments):
    """Returns header text describing the argument type and containing the search string if one exists."""
    if command_line_arguments.listAthletesFromNOC:
        return "The athletes from " + command_line_arguments.listAthletesFromNOC + " are:\n\nAthlete name\n================"
    elif command_line_arguments.listGoldMedalsOfNOCs:
        return "The number of gold medals each NOCs has, showing NOC with the most first:\n\nGold medals | NOC name\n================"
    elif command_line_arguments.listTopAthletesOfSport:
        return "The athletes with gold medals in " + command_line_arguments.listTopAthletesOfSport + " from most medals to least:\n\nGold medals | Athlete name\n================"
    return None

def get_formated_row(row):
    """Converts and returns the passed list into a formated string."""
    formated_row = ""
    if len(row) > 1:
        number_spaces = 5 - len(str(row[1]))
        formated_row = formated_row + str(row[1]) + (' ' * number_spaces) + "| "
    if not row[0]:
        return formated_row
    return formated_row + row[0]

"""Executes the main program."""
main()
