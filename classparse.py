#! /usr/local/bin/python

import requests
import sys,logging
import optparse
import cookielib
import re
import mechanize

from BeautifulSoup import BeautifulSoup
from requests import session

TEMPLATE = """%(section)s %(course)s %(crn)s %(title)s %(time)s %(instructor)s %(op_spots)s"""

class ClassParse:
	def __init__(self):
		#self.username = sys.argv[1]
		#self.password = sys.argv[2]
		self.html = ''

	def fetchResults(self):

		#Fetch names of subjects you want to query
		subjects = [line.strip() for line in open('subjects.txt')]


		#logger = logging.getLogger("mechanize")
		#logger.addHandler(logging.StreamHandler(sys.stdout))
		#logger.setLevel(logging.DEBUG)

		print subjects

		#Browser
		br = mechanize.Browser()

		#Options

		br.set_handle_equiv(True)
		#br.set_handle_gzip(True)
		br.set_handle_redirect(mechanize.HTTPRedirectHandler)
		br.set_handle_referer(True)
		#br.set_debug_redirects(True)
		#br.set_debug_http(True)


		#Refresh

		br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

		#Headers
		br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

		#Open ND Login Page
		#br.open("https://was.nd.edu/reg/srch/loginPage.jsp")
		#br.select_form(nr=0)

		#Testing the output of the Form
		#print br

		#Inserts username information
		#br['j_username'] = self.username
		#br['j_password'] = self.password
		#br.submit()

		#Open ClassSearch Page
		br.open("https://was.nd.edu/reg/srch/ClassSearchServlet")

		#What page are we on?
		print br.geturl()

		#Index.html page 
		assert br.viewing_html()
		print br.title()

		#CLick here to get started with ClassSearch
		#response = br.follow_link(nr=0)
		#print response.read()

		print br.title()

		br.select_form(nr=0)

		#forms = [f for f in br.forms()]

		#form = forms[0]

		#print form

		#print br.controls[3].name


		#Used for iterating over all subjects in the list, for selection purposes later
		#for c in br.controls[3].items:
		#	print c.name

		br.set_all_readonly(False)

		br.set_value(subjects,name="SUBJ")


		response = br.submit()
		self.html = response.read()

		#self.parse(self.html)

	def parse(self, html):
		soup = BeautifulSoup(self.html)

		table1 = soup.find('table', {'id': 'resulttable'})
		table2 = table1.find('tbody')

		for row in table2.findAll('tr'):
			#print row
			cells = row.findAll('td')



			crn = cells[7].text
			title = cells[1].text
			time = cells[10].text
			instructor = cells[9].text
			op_spots = int(cells[5].text)
			course = cells[0].text

			#Separate first and last name of instructor
			i_first = self.getInstructorFirst(instructor)
			i_last = self.getInstructorLast(instructor)

			course_no = self.getCourse(course)
			section = self.getSection(course)

			if(op_spots > 0):
				yield {
				'section': section,
				'course': course_no,
				'crn': crn,
				'title': title,
				'time': time,
				'instructor': instructor,
				'op_spots': op_spots,
				}

	def showResults(self):

		for listing in self.parse(self.html):
			print TEMPLATE % listing

	def getInstructorFirst(self, instructor):
		name = instructor.partition(',')
		last = name[0]
		first = name[2][1:]
		#print first + ' ' + last

		return first

	def getInstructorLast(self, instructor):
		name = instructor.partition(',')
		last = name[0]

		return last

	def getCourse(self, course):

		entry = course.partition('-')
		co_no = entry[0]
		section = entry[2]

		course_no = re.sub('[^A-Za-z0-9]+', '', co_no)
		section = re.sub('[^0-9]', '', section)

		#print section + ' ' + cono

		return course_no

	def getSection(self, course):

		entry = course.partition('-')
		section = entry[2]

		section = re.sub('[^0-9]', '', section)

		return section


