"""
This script runs the UnitTestAnalysis application using a development server.
"""

from os import environ
from UnitTestAnalysis import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.debug = True

    app.run(HOST, PORT)
