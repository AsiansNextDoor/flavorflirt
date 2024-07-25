#!/usr/bin/env python3
"""Working with SQLite3"""

import csv
import logging
import sqlite3
import sys
import click
import ast


@click.command(help="Create a database from the CSV file")
@click.argument("db_name")
@click.option("--datafile", default="index.csv")
def create(db_name: str, datafile: str) -> None:
    """Create database"""
    with sqlite3.connect(db_name) as conn:
        with open(datafile, "r") as f:
            data = list(csv.DictReader(f))
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS dishes;")
            cursor.execute(
                "CREATE TABLE dishes ("
                + "id integer not null primary key,"
                + "country,"
                + "description,"
                + "id_ integer,"
                + "keywords"
                + "is_shoppable"
                + "language"
                + "name"
                + "slug"
                + "video_url"
                + "is_licensed_video"
                + "is_community"
                + "thumbnail_url"
                + "inspired_by"
                + "linked_recipes"
                + "tags"
                + "cook_time"
                + "prep_time"
                + "total_time"
                + "ratings_negative"
                + "ratings_positive"
                + "score"
                + "protein"
                + "fat"
                + "calories"
                + "sugar"
                + "carbohydrates"
                + "fiber"
                + ");"
            )
            # print(tuple(a.values() for a in data))
            cursor.executemany(
                "INSERT INTO dishes VALUES(?, ?, ?, ?, ?);",
                (tuple(a.values()) for a in data),
            )


# @click.command(help="Read all records from the specified table")
# @click.argument("db_name")
# @click.option("--table", "-t", default="dishes")
def read(db_name: str, table: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        d = []
        keys = [desc[0] for desc in cursor.description]
        for record in cursor:
            row = {}
            for k, v in zip(keys, record):
                row[k] = v
            d.append(row)
        return d

def find_user(db_name: str, table: str, username: str, password: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE username = ?;"
        cursor.execute(query, (username,))
        return not cursor.fetchone() is None

def verify_user(db_name: str, table: str, username: str, password: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE username = ? AND password = ?;"
        cursor.execute(query, (username, password))
        return not cursor.fetchone() is None
    
def add_user(db_name: str, table: str, username: str, password: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} values('{username}', '{password}');")
    return True

def modify(db_name: str, table: str, username: str, lists):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        query = f"DELETE FROM {table} WHERE username = ?"
        cursor.execute(query, (username,))
        insert_query = f"INSERT INTO {table} (username, lists) VALUES (?, ?)"
        cursor.execute(insert_query, (username, str(lists)))
    return True

def read_list(db_name: str, table: str, username: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        query = f"SELECT lists FROM {table} WHERE username = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        
        if row:
            return ast.literal_eval(row[0])
        else:
            return False

@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="dishes")
@click.option("--location", "-l", default="", help="Location to read")
@click.option("--species", "-s", default="", help="Species to read")
def query(db_name: str, table: str, species: str, location: str) -> None:
    """Query records"""
    ...


@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="dishes")
@click.option("--dishes", "-a", help="dishes to update", type=int, default=0)
def update(db_name: str, table: str, dishes: int) -> None:
    """Update records"""
    ...


@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="dishes")
@click.option("--dishes", "-a", help="dishes to update", type=int, default=0)
@click.option("--species", "-s", default="", help="Species to delete")
def delete(db_name: str, table: str, dishes: int, species: str) -> None:
    """Delete records"""
    ...


@click.group()
@click.option("--verbose", "-v", is_flag=True, default=False)
def cli(verbose: bool):
    """Command-line interface"""
    if verbose:
        logging.basicConfig(level=logging.INFO)


def main():
    """Main function"""
    cli.add_command(create)
    # cli.add_command(read)
    # cli.add_command(query)
    # cli.add_command(update)
    # cli.add_command(delete)
    # cli()


if __name__ == "__main__":
    main()