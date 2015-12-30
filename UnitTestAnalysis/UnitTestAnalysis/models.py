from UnitTestAnalysis import app, cnxn

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
                               'ErrorMessage':row[7]
                               } for row in rows if row[6] is None]

        analyzed_result = [{'ClassName':row[1],
                               'TestName':row[2],
                               'Type':row[3],
                               'Result':row[5],
                               'TFSBugID':row[6],
                               'ErrorMessage':row[7]
                               } for row in rows if row[6] is not None]

        return (unanalyzed_result, analyzed_result)


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
        sp_str = 'exec dbo.FindResultsPerTestMethod ?, ?, ?'
        #call stored procedure
        records = [{'Date':row[0],
                               'Build':row[1],
                               'Branch':row[2],
                               'Result':row[5],
                               'ErrorMessage':row[8]
                               } for row in self.execute_stored_procedure(sp_str)]

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