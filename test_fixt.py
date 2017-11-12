import pytest
import allure
import logging

class TestFixt:

	@pytest.fixture(scope = 'session', autouse = True)
	def ses(self,request):
		print('setting logger')
		logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] \
		 %(message)s', filename = u'/var/log/pytest.log', level = logging.DEBUG)


	@pytest.fixture(scope = 'function', autouse = True)
	def pr2(self,request):
		print('fixture pr2 setup')
		yield
		print ('fisture pr2 teqrdown')


	@pytest.fixture(scope = 'function', autouse = True)
	def pr1(self,request):
		if 'body' in request.keywords.keys():
			print('pass pr1')
			return
		print('fixture pr1 setup')
		yield
		print ('fisture pr1 teqrdown')

	@pytest.fixture(scope = 'function')
	def pr3(self,request):
		print('fixture pr3')
		yield
		print('teardown pr3')
		
	@pytest.allure.testcase('test.tes')
	@pytest.allure.testcase('http://my.tms.org/TESTCASE-1')
	@allure.issue('http://jira.lan/browse/ISSUE-2')
	@allure.issue('http://jira.lan/browse/ISSUE-1')
	@pytest.allure.BLOCKER
	def test_1(self,pr3):
		print('body')
		logging.error('WTF')
		logging.debug('asfsafsa')
		assert False

	@pytest.allure.testcase('http://my.tms.org/TESTCASE-1')
	@allure.issue('http://jira.lan/browse/ISSUE-2')
	@pytest.allure.MINOR
	def test_2(self):
		print('body2')