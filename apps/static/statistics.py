from django.db import connection


def execute_statement(statement):
    cursor = connection.cursor()
    cursor.execute(statement)
    data = cursor.fetchall()
    return data
