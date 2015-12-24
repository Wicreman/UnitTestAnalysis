"""
The flask application package.
"""

from flask import Flask
import pyodbc
app = Flask(__name__)
# Conenct MSSQL by using pyodbc with DSN
cnxn = pyodbc.connect('DSN=UT;Trusted_Connection=yes')

import UnitTestAnalysis.views
