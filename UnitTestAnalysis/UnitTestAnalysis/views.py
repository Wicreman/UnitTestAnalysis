"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for
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
            tfs_bug_id = row[6]
            if  tfs_bug_id is None:
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
        build=build,
    )

'''
    Will update the Unit Test Failure table with the TFS Bug ID for the specified failed Test method.
    Parameter 1 Required varchar(50) - Build Number.
    Parameter 2 Required varchar(max) - Unit Test Class Name.
    Parameter 3 Required varchar(max) - Unit Test Method Name.
    Parameter 4 Required BIGINT - TFS Bug ID.
    exec dbo.AnalyzeTestMethodToTFSBug '6.3.3000.231','VersioningPurchaseOrderTest','testConfirm', 3711250
'''
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        build = request.form['build']
        class_name = request.form['classname']
        test_name = request.form['testname']
        bug_id = request.form['bugid']
        if bug_id is not None:
            # init stored procedure parmater
            values = (build, class_name, test_name, bug_id)
            cursor = cnxn.cursor()
            if cursor is not None:
                # init query string
                sql_str = 'dbo.AnalyzeTestMethodToTFSBug ?,?,?,?'
                # call stored procedure 
                cursor.execute(sql_str, (values))
                # call commit to update the data
                cnxn.commit()
    
    return redirect(url_for('detail', build=build))


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/query')
def query():
    """
    Display all results for a given unit test.
    Parameter 1 Required varchar(max) - Unit Test Class Name.
    Parameter 2 Required varchar(max) - Unit Test Method Name.
    Parameter 3 Optional varchar(10)  - Enter '6.2%' for R2 or nothing for R3 as that is the default value.
    exec dbo.FindResultsPerTestMethod 'DMFDefinitionGroupServiceTest','testcreate ','6.3%'
    """
    #Unit Test Class Name
    class_name = request.args.get('classname', '')
    #Unit Test Method Name
    test_name = request.args.get('testname', '')
    #Enter '6.2%' for R2 or nothing for all
    branch = request.args.get('branch', '6%')
    
    # save query result
    result =[]
    if class_name and test_name:
        # init cursor
        cursor = cnxn.cursor()
        
        if cursor is not None:
            # init stored procedure parmater
            values = (class_name, test_name, branch )
            # init query string
            sql_str = 'exec dbo.FindResultsPerTestMethod ?, ?, ?'
            # call stored procedure 
            cursor.execute(sql_str, (values))
            # fetch all rows 
            rows = cursor.fetchall()
            #TODO: move DB logic to common class
            # save the requried fields to result
            for row in rows:
                result.append({'Date':row[0],
                               'Build':row[1],
                               'Branch':row[2],
                               'Result':row[5],
                               'ErrorMessage':row[8]
                               })
    return render_template(
        'query.html',
        title='Display all results for a given unit test',
        records=result,
        className=class_name,
        testName=test_name
    )
