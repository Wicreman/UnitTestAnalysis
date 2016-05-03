import os
from xml.etree import ElementTree as ET
from UnitTestAnalysis import APP_ROOT, db
from UnitTestAnalysis.models import UnitTestCase

class Utility(object):
    """ """
    wicesoft_feature = ['BestPracticeTool', 'XPlusPlusLanguage', 'ES', 
                         'Client','Procure','Control', 
                         'Workflow', 'Server', 'Catalog', 
                         'Sales', 'Sourcing', 'SetupUpgrade', 
                         'AIF', 'DeveloperAndPartnerTools', 'Infrastructure', 
                         'Process', 'ProcessIndustries2', 'TradeSource', 
                         'Transportation', 'InventoryMgmt', 'Manufacturing', 
                         'ProductMgmt', 'BIAndReporting', 'Retail', 
                         'EP', 'DO', 'BAServiceApp', 
                         'DMFTest',  'Warehouse', 'WarehouseMgmt',
                         'Connector', 'AppConfigService']

    # 初始化root 节点，并且初始化branch
    def __init__(self, filename, branch):
        self.root = ET.parse(os.path.join(APP_ROOT, filename)).getroot()
        self.branch = branch

    #获取所有case
    def parseXML(self):
        log = ''
        for child_of_root in self.root.findall('.//test-suite'):
            suite_name = child_of_root.attrib['name']
            if "TestProject_" in suite_name:
                log += "Processing "+ suite_name + '\n'

                start_index = suite_name.index('_') +1
                feature = suite_name[start_index:]
                if feature in self.wicesoft_feature:
                    company = 'Wicresoft'
                else:
                    company = 'Sonata'

                for test_case in child_of_root.findall('.//test-case'):
                    if test_case is not None:
                        fullname = test_case.attrib['name']
                        classname_testname = fullname.split('.')
                        class_name = classname_testname[0]
                        test_name = classname_testname[1]
                        utc = UnitTestCase(class_name,test_name,self.branch,feature,company)
                        db.session.add(utc)
                        db.session.commit()
                        
                        log += "Successfully added " + fullname + '\n'

                        
        return log


