#authors: Kai Johnson

import sys
import argparse
import flask
import json
import psycopg2
import psycopg2.extras
from config import database, user, password

app = flask.Flask(__name__)

@app.route('/nocs')
def get_nocs():
    query = get_nocs_query()
    cursor = query_database(query)
    list_of_nocs = convert_cursor_to_list_of_dictionaries(cursor, 0)
    return json.dumps(list_of_nocs)

def get_nocs_query():
    query = '''SELECT DISTINCT
          national_olympic_committees.abbreviation,
          national_olympic_committees.country
      FROM
          national_olympic_committees
      ORDER BY
          national_olympic_committees.abbreviation'''
    return [query]

def query_database(query):
    connection = get_database_connection()
    cursor = ""
    try:
        cursor = connection.cursor()
        if len(query) == 1:
            cursor.execute(query[0])
        else:
            print(query[1])
            cursor.execute(query[0], (query[1],))
    except Exception as e:
        print(e)
    return cursor

def get_database_connection():
    connection = ""
    try:
        connection = psycopg2.connect(database=database, user=user, password=password)
    except Exception as e:
        print(e)
    return connection

def convert_cursor_to_list_of_dictionaries(cursor, key_index):
    list = []
    for row in cursor:
        dictionary = {}
        values = []
        for i in range(0, len(row)):
            if i != key_index:
                values.append(row[i])
        dictionary[row[key_index]] = values

        #dictionary[row[0]] = row[1]
        list.append(dictionary)
    return list

@app.route('/games')
def get_games():
    query = get_games_query()
    cursor = query_database(query)
    list_of_games = convert_cursor_to_list_of_dictionaries(cursor, 1)
    return json.dumps(list_of_games)

def get_games_query():
    query = '''SELECT
      olympic_games.id,
      olympic_games.year,
      olympic_games.season,
      olympic_games.city
    FROM
      olympic_games
    ORDER BY
      olympic_games.year'''
    return query

@app.route('/medalists/games/<games_id>')
def get_medalists(games_id):
    noc_abbreviation = flask.request.args.get('noc', default='-1')
    print(noc_abbreviation)
    query = get_medalists_query(games_id, noc_abbreviation)
    cursor = query_database(query)
    has_result = True
    count = 0
    if cursor.rowcount > 0:
        list_of_medalists = convert_cursor_to_list_of_dictionaries(cursor, 1)
        return json.dumps(list_of_medalists)
    else:
        return 'There were no medalists in this instance.'

def get_medalists_query(games_id, noc_abbreviation):
    query = ''
    if noc_abbreviation == '-1':
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
              olympic_games.id = ''' + str(games_id) + ''' AND
              linking_table.medal_id = medals.id AND
              medals.medal != 'NA' AND
              linking_table.athlete_id = athletes.id AND
              linking_table.sport_id = sports.id AND
              linking_table.event_id = events.id'''
        return [query]
    else:
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
    host = 'localhost'
    port = 5000
    app.run(host = host, port = port, debug = True)
