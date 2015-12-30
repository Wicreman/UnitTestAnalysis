"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for
from UnitTestAnalysis import app, cnxn
from UnitTestAnalysis.models import DBHelper

@app.route('/')
@app.route('/home')
def home():
    """Display the high level results for last N UT Runs"""
   
    # init stored procedure parmater
    values = (20, '6%')
    db_helper = DBHelper(values)
    result = db_helper.find_top_n_build()

    return render_template(
        'index.html',
        title='Home Page',
        records  = result,
    )


@app.route('/detail/<build>')
def detail(build):
    '''
    Display the Detailed Failure results for a given Build.
    exec dbo.FindFailuresPerBuild '6.3.3000.231'
    Parameter 1 Required varchar(50)- Build Number for a unit test run. 
    '''
    db_helper = DBHelper(build)
    # call stored procedure 
    (unanalyzed_result, analyzed_result) = db_helper.find_failures_per_build()

    return render_template(
        'detail.html',
        title='Find Failures Per Build',
        unanalyzed_records  = unanalyzed_result,
        analyzed_records  = analyzed_result,
        build=build,
    )


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    '''
    Will update the Unit Test Failure table with the TFS Bug ID for the specified failed Test method.
    Parameter 1 Required varchar(50) - Build Number.
    Parameter 2 Required varchar(max) - Unit Test Class Name.
    Parameter 3 Required varchar(max) - Unit Test Method Name.
    Parameter 4 Required BIGINT - TFS Bug ID.
    exec dbo.AnalyzeTestMethodToTFSBug '6.3.3000.231','VersioningPurchaseOrderTest','testConfirm', 3711250
    '''
    if request.method == 'POST':
        build = request.form['build']
        class_name = request.form['classname']
        test_name = request.form['testname']
        bug_id = request.form['bugid']
        if bug_id is not None:
            # init stored procedure parmater
            values = (build, class_name, test_name, bug_id)
            db_helper = DBHelper(values)
            db_helper.analyze_test_method_to_tfsbug()
            
    return redirect(url_for('detail', build=build))


@app.route('/todolist')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
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
        values = (class_name, test_name, branch )
        db_helper = DBHelper(values)
        result = db_helper.find_result_per_test_method()[0:60]
        
    return render_template(
        'query.html',
        title='Display all results for a given unit test',
        records=result,
        className=class_name,
        testName=test_name
    )
