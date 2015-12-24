"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from UnitTestAnalysis import app, cnxn

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    # init cursor
    cursor = cnxn.cursor()
    # save query result
    result =[]
    if cursor is not None:
        # Top number
        count = 20
        # Which main build like 6.3 or 6.2
        main_build = "6%"
        # init stored procedure parmater
        values = (count, main_build)
        # init query string
        sql_str = 'exec dbo.FindTopNBuilds ?, ?'
        # call stored procedure 
        cursor.execute(sql_str, (values))
        # fetch all rows 
        rows = cursor.fetchall()
        #TODO: move DB logic to common class
        # save the requried fields to result
        for row in rows:
            result.append({'Build':row[0],
                           'Date':row[1],
                           'Branch':row[2],
                           'NonCIT_failed':row[6],
                           'CIT_failed':row[8],
                           'Not_run':row[9],
                           'Passed_rate':row[10]
                           })

    return render_template(
        'index.html',
        title='Home Page',
        records  = result,
    )

'''
Display the Detailed Failure results for a given Build.
exec dbo.FindFailuresPerBuild '6.3.3000.231'
Parameter 1 Required varchar(50)- Build Number for a unit test run. 
'''
@app.route('/detail/<build>')
def detail(build):
    # init cursor
    cursor = cnxn.cursor()
    # save query result
    result =[]
    if cursor is not None:
        # init query string
        sql_str = 'dbo.FindFailuresPerBuild  ?'
        # call stored procedure 
        cursor.execute(sql_str, build)
        # fetch all rows 
        rows = cursor.fetchall()
        #TODO: move DB logic to common class
        # save the requried fields to result
        for row in rows:
            result.append({'ClassName':row[1],
                           'TestName':row[2],
                           'Type':row[3],
                           'Result':row[5],
                           'TFSBugID':row[6],
                           'ErrorMessage':row[7]
                           })

    return render_template(
        'detail.html',
        title='Find Failures Per Build',
        records  = result,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
