'''Authors: Kai Johnson
Date: 02/02/2021
A introduction to APIs using the Olympics database designed last week.
'''

import flask
import json
import psycopg2
from config import database, user, password

app = flask.Flask(__name__)

@app.route('/nocs')
def get_nocs():
    '''Returns a list of dictionaries, each of which represents one National Olympic Committee, alphabetized by NOC abbreviation.'''
    query = get_nocs_query()
    cursor = query_database(query)
    list_of_nocs = convert_cursor_to_list_of_dictionaries(cursor)
    return json.dumps(list_of_nocs)

@app.route('/games')
def get_games():
    '''Returns a list of dictionaries, each of which represents one Olympic games, sorted by year.'''
    query = get_games_query()
    cursor = query_database(query)
    list_of_games = convert_cursor_to_list_of_dictionaries(cursor)
    return json.dumps(list_of_games)

@app.route('/medalists/games/<games_id>')
def get_medalists(games_id):
    '''Returns a list of dictionaries, each representing one athlete who earned a medal in the specified games.  If a GET parameter refering to a noc abbreviation is present, returns only those medalists who were on the specified NOC's team during the specified games.'''
    noc_abbreviation = flask.request.args.get('noc', default='-1')
    query = get_medalists_query(games_id, noc_abbreviation)
    cursor = query_database(query)
    if cursor.rowcount > 0:
        list_of_medalists = convert_cursor_to_list_of_dictionaries(cursor)
        return json.dumps(list_of_medalists)
    else:
        return 'There were no medalists in this instance.'

def query_database(query):
    '''Executes the passed query and returns the resulting cursor or prints an error message and returns an empty string if the query failed.'''
    connection = get_database_connection()
    cursor = ""
    try:
        cursor = connection.cursor()
        if len(query) == 1:
            cursor.execute(query[0])
        else:
            cursor.execute(query[0], (query[1],))
    except Exception as e:
        print(e)
    return cursor

def get_database_connection():
    '''Returns a connection to a database specified by 'config.py'.'''
    connection = ""
    try:
        connection = psycopg2.connect(database=database, user=user, password=password)
    except Exception as e:
        print(e)
    return connection

def convert_cursor_to_list_of_dictionaries(cursor):
    '''Takes the passed cursor object and creates a list of dictionaries, with each dictionary representing one row of the cursor and the keys refering to the first item in the row.'''
    list = []
    for row in cursor:
        dictionary = {}
        if len(row) > 2:
            values = []
            for i in range(1, len(row)):
                values.append(row[i])
            dictionary[row[0]] = values
        else:
            dictionary[row[0]] = row[1]
        list.append(dictionary)
    return list

def get_nocs_query():
    '''Returns the SQL script that retrieves all NOCs in the database.'''
    query = '''SELECT DISTINCT
          national_olympic_committees.abbreviation,
          national_olympic_committees.country
      FROM
          national_olympic_committees
      ORDER BY
          national_olympic_committees.abbreviation'''
    return [query]

def get_games_query():
    '''Returns the SQL script that retrieves all the olympic games in the database.'''
    query = '''SELECT
      olympic_games.id,
      olympic_games.year,
      olympic_games.season,
      olympic_games.city
    FROM
      olympic_games
    ORDER BY
      olympic_games.year'''
    return [query]

def get_medalists_query(games_id, noc_abbreviation):
    '''Retrieves the SQL script that retrieves all the medalists at a specified game and (if applicable) belonging to a particular NOC.'''
    query = ''
    if noc_abbreviation == '-1':
        return get_medalist_query_without_noc(games_id)
    else:
        return get_medalist_query_with_noc(games_id, noc_abbreviation)

def get_medalist_query_without_noc(games_id):
    query = '''SELECT
          athletes.id,
          athletes.name,
          athletes.sex,
          sports.sport,
          events.event_title,
          medals.medal
      FROM
          linking_table,
          sports,
          events,
          athletes,
          medals,
          olympic_games
      WHERE
          linking_table.olympic_game_id = olympic_games.id AND
          olympic_games.id = %s AND
          linking_table.medal_id = medals.id AND
          medals.medal != 'NA' AND
          linking_table.athlete_id = athletes.id AND
          linking_table.sport_id = sports.id AND
          linking_table.event_id = events.id'''
    return [query, games_id]

def get_medalist_query_with_noc(games_id, noc_abbreviation):
    query = '''SELECT
          athletes.id,
          athletes.name,
          athletes.sex,
          sports.sport,
          events.event_title,
          medals.medal
      FROM
          linking_table,
          sports,
          events,
          athletes,
          medals,
          national_olympic_committees,
          olympic_games
      WHERE
          linking_table.olympic_game_id = olympic_games.id AND
          olympic_games.id = ''' + str(games_id) + ''' AND
          linking_table.national_olympic_committee_id = national_olympic_committees.id AND
          national_olympic_committees.abbreviation = %s AND
          linking_table.medal_id = medals.id AND
          medals.medal != 'NA' AND
          linking_table.athlete_id = athletes.id AND
          linking_table.sport_id = sports.id AND
          linking_table.event_id = events.id'''
    return [query, noc_abbreviation]

if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host = host, port = port, debug = True)
