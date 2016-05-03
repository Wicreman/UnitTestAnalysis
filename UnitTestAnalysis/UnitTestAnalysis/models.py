from UnitTestAnalysis import app, cnxn, db

class DBHelper(object):
    """Helper method for database actions"""

    # Initialize method with stored procedure parmater
    def __init__(self, values):
        self.values = values


    def execute_stored_procedure(self, sp_str, is_commit=False):
        '''
        Execute stored procedure by using sp string
        sp_str: stored procedure string
        '''
        try:
        # Initialize cursor
            cursor = cnxn.cursor()
            if cursor is not None:
                # call stored procedure
                cursor.execute(sp_str, self.values)
                if is_commit:
                     # call commit to update the data
                    cnxn.commit()
                    return None
                 # fetch all rows
                return cursor.fetchall()
        except ConnectionAbortedError as con:
            app.logger(con.strerror)
        finally:
            cursor.close()

        return None


    def find_top_n_build(self):
        '''
        -- Display the high level results for last N UT Runs.
        -- Parameter 1 Optional int - Number of latest build you want to see. Default is 5.
        -- Parameter 2 Optional varchar(10) - Version of the product. Default is '6.3%'.
        --
        exec dbo.FindTopNBuilds 20,'6%'
        '''
        # init query string
        sp_str = 'exec dbo.FindTopNBuilds ?, ?'
        records = [dict(Build=row[0],
            Date= row[1], 
            Branch=row[2], 
            NonCIT_failed=row[6], 
            CIT_failed=row[8], 
            Not_run=row[9], 
            Passed_rate=row[10]) 
                   for row in self.execute_stored_procedure(sp_str)]

        return records
           
    def get_area(self, classname, testname):
        """ get the featur and owner of test cases"""
        # Get the build to find the branch
        build = self.values
        if "6.3" in build:
            branch = "DAX63SE"
        else:
            branch = "DAX62CD"

        feature =''
        company = ''

        testcase = UnitTestCase.query.filter_by(classname=classname, testname=testname,branch=branch).first()
        if testcase:
            feature = testcase.feature
            company = testcase.company

        return (feature, company)


    def find_failures_per_build(self):
        '''
        -- Display the Detailed Failure results for a given Build.
        -- Parameter 1 Required varchar(50)- Build Number for a unit test run. 

        exec dbo.FindFailuresPerBuild '6.3.3000.721'
        '''
        # init query string
        sp_str = 'dbo.FindFailuresPerBuild  ?'
        #call stored procedure
        rows = self.execute_stored_procedure(sp_str)
        
        unanalyzed_result = [{'ClassName':row[1],
                               'TestName':row[2],
                               'Type':row[3],
                               'Result':row[5],
                               'TFSBugID':row[6],
                               'ErrorMessage':row[7],
                               'Area':self.get_area(row[1],row[2])
                               } for row in rows if row[6] is None]

        analyzed_result = [{'ClassName':row[1],
                               'TestName':row[2],
                               'Type':row[3],
                               'Result':row[5],
                               'TFSBugID':row[6],
                               'ErrorMessage':row[7]
                               } for row in rows if row[6] is not None]

        return (unanalyzed_result[:200], analyzed_result[:200])


    def analyze_test_method_to_tfsbug(self):
        '''
        -- Will update the Unit Test Failure table with the TFS Bug ID for the specified failed Test method.
        -- Parameter 1 Required varchar(50) - Build Number.
        -- Parameter 2 Required varchar(max) - Unit Test Class Name.
        -- Parameter 3 Required varchar(max) - Unit Test Method Name.
        -- Parameter 4 Required BIGINT - TFS Bug ID.
        --
        exec dbo.AnalyzeTestMethodToTFSBug '6.3.3000.231','VersioningPurchaseOrderTest','testConfirm', 3711250
        '''
        # init query string
        sp_str = 'dbo.AnalyzeTestMethodToTFSBug ?,?,?,?'
        #call stored procedure
        self.execute_stored_procedure(sp_str,True)

    def find_result_per_test_method(self):
        '''
        -- Display all results for a given unit test.
        -- Parameter 1 Required varchar(max) - Unit Test Class Name.
        -- Parameter 2 Required varchar(max) - Unit Test Method Name.
        -- Parameter 3 Optional varchar(10)  - Enter '6.2%' for R2 or nothing for R3 as that is the default value.
        --
        exec FindResultsPerTestMethod 'DMFDefinitionGroupServiceTest','testcreate ','6.3%'
        '''
        # init query string
        records = []
        TFSbug_id = None
        class_name = self.values[0]
        test_name = self.values[1]
        sp_str = 'exec dbo.FindResultsPerTestMethod ?, ?, ?'
        rows = self.execute_stored_procedure(sp_str)
        for row in rows:
            if row[5] == 'Failed':
                self.values = (row[1], class_name, test_name)
                for bug_id in self.execute_stored_procedure("""
                                          select C.TFSBugID
                                          from 
                                          UnitTestRun A 
                                          Join UnitTestRunTestCase B ON (A.RecordID = B.UnitTestRunID)
									      Join UnitTestRunTestCaseFailure C ON(B.RecordID = C.UnitTestRunTestCaseID)
                                          where
                                          A.Build = ?
                                          and B.ClassName = ?
	                                      and   B.TestName = ?
	                                     """):
                    if bug_id is not None:
                        TFSbug_id = bug_id.TFSBugID

            records.append({'Date':row[0],
                               'Build':row[1],
                               'Branch':row[2],
                               'Result':row[5],
                               'ErrorMessage':row[8],
                               'TFSBugID': TFSbug_id})
        '''
        #call stored procedure
        records = [{'Date':row[0],
                               'Build':row[1],
                               'Branch':row[2],
                               'Result':row[5],
                               'ErrorMessage':row[8]
                               } for row in self.execute_stored_procedure(sp_str)]
        '''
        return records
    
    def mark_as_passed(self):
        '''
        Will update the UnitTestRunTestCase table with the status for the specified failed Test method.
        Parameter 1 Required varchar(50) - Build Number.
        Parameter 2 Required varchar(max) - Unit Test Class Name.
        Parameter 3 Required varchar(max) - Unit Test Method Name.
        exec 
        UPDATE dbo.UnitTestRunTestCase
        SET Success = 1
        from 
          UnitTestRun A 
          Join UnitTestRunTestCase B ON (A.RecordID = B.UnitTestRunID)
        where
          B.ClassName = 'KanbanJobSchedulerPlanTest'
	    and   B.TestName = 'testCanPostponeKanbanJobMove'
	    and A.Build = '6.3.3000.721'
        '''

        #call stored procedure
        self.execute_stored_procedure("""
                                    UPDATE dbo.UnitTestRunTestCase
                                    SET Success = 1
                                    from 
                                      UnitTestRun A 
                                      Join UnitTestRunTestCase B ON (A.RecordID = B.UnitTestRunID)
                                    where
                                    A.Build = ?
                                    and B.ClassName = ?
	                                and   B.TestName = ?
	                                 """, True)

    def find_new_failures(self):
        '''
        -- 
        -- This query will contrast two result sets and return only the Failing unit tests from the New Build that have different results from the baseline build.
        -- Parameter 1 Required varchar(50) - New Build Number.
        -- Parameter 2 Required varchar(50) - Baseline Build Number for comparison.
        --
        exec dbo.FindNewFailuresBetweenBuilds '6.3.1000.2359','6.3.1000.2509' 
        '''
        # init query string
        sp_str = 'dbo.FindNewFailuresBetweenBuilds  ?, ?'
        #call stored procedure
        rows = self.execute_stored_procedure(sp_str)

        result = [{'ClassName':row[0],
                               'TestName':row[1],
                               'Type':row[2],
                               'Result':row[5],
                               'BaselineResult':row[6],
                               'TFSBugID':row[7],
                               'ErrorMessage':row[8]
                               } for row in rows]

        unanalyzed_result = [{'ClassName':row[0],
                               'TestName':row[1],
                               'Type':row[2],
                               'Result':row[5],
                               'BaselineResult':row[6],
                               'TFSBugID':row[7],
                               'ErrorMessage':row[8]
                               } for row in rows if row[7] is None]

        analyzed_result = [{'ClassName':row[0],
                               'TestName':row[1],
                               'Type':row[2],
                               'Result':row[5],
                               'BaselineResult':row[6],
                               'TFSBugID':row[7],
                               'ErrorMessage':row[8]
                               } for row in rows if row[7] is not None]

        return (unanalyzed_result[:200], analyzed_result[:200])

    def analyze_with_baseline_bug(self):
        '''
        -- 
        -- This query will Copy the TFSBugID from the Baseline Record to the New Failure record if the failures are identical.
        -- Parameter 1 Required varchar(50) - New Build Number.
        -- Parameter 2 Required varchar(50) - Baseline Build Number for comparison.
        --
        exec dbo.CopyTFSBugIdFromBaselineToNewFailureWhenIdentical '6.2.3000.684','6.2.3000.751'
        '''
        # init query string
        sp_str = 'dbo.CopyTFSBugIdFromBaselineToNewFailureWhenIdentical ?,?'
        #call stored procedure
        self.execute_stored_procedure(sp_str,True)


class UnitTestCase(db.Model):
    """Unit Test Case Model """
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(120))
    testname = db.Column(db.String(120))
    branch = db.Column(db.String(80))  # DAX62HF, DAX63HF
    feature = db.Column(db.String(80))
    company = db.Column(db.String(120)) # Wicresoft, Sonata

    def __init__(self, classname, testname,branch,feature,company):
        self.classname = classname
        self.testname = testname
        self.branch = branch
        self.feature = feature
        self.company = company

    def __repr__(self):
        return '<UnitTestCase %r>' % self.company

