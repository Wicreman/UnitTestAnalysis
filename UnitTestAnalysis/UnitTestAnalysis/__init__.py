"""
The flask application package.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from xml.etree import ElementTree  as ET
import pyodbc
import os
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1/utc'

db = SQLAlchemy(app)
# Conenct MSSQL by using pyodbc with DSN
cnxn = pyodbc.connect('DSN=UT;Trusted_Connection=yes')
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top




import UnitTestAnalysis.views
