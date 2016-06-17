import urllib2
import lxml.html
import json
from lxml import etree
import googlemaps
import os, sys, getopt, re

# Initial Vars
baseurl = os.getenv('RANK_URL','http://ontario.compareschoolrankings.org')
gmaps = googlemaps.Client(key=os.getenv('GMAP_API_KEY'))

def get_element_data(school_url):
	print "connecting to "+school_url
	try:
		page = urllib2.urlopen(school_url).read()
	except:
		print "couldn\'t open url: " + school_url
		na_data = { 'Type' : 'n/a', 'Address' : 'n/a', 'Phone' : 'n/a', 'District' : 'n/a'}
		return na_data
	try: 
		html = lxml.html.fromstring(page)

		element = html.get_element_by_id('ctl00_ContentPlaceHolder1_SchoolInfoDisplay') 

		basic_info = [i for i in element.itertext()]

		data = {}
		# The Type of School: Private, Public, Catholic is located at the second position
		data["Type"] = basic_info[1]
		#  Assemble the address
		data["Address"] = re.sub("\sBox\s+\d+|\sC.?P.?\s+\d+|\sGeneral Delivery","", basic_info[2].strip() + ", " + basic_info[3].strip() + ', Canada')
		# Getting the Phone Number
		data["Phone"] = basic_info[4].split(":")[1].strip()
		# Getting the School District
		data["District"] = basic_info[5].split(":")[1].strip()
	except:
		print "Error trying to parse basic info for: " + school_url
		na_data = { 'Type' : 'n/a', 'Address' : 'n/a', 'Phone' : 'n/a', 'District' : 'n/a'}
		return na_data

	try:
		element = html.get_element_by_id('ctl00_ContentPlaceHolder1_detailedReportCard_SchoolProperties1_tblProps')
		counter = 0
		header_tmp = ''
		for e in element.iter('td'):
			if e.keys()[0] == 'width':
				if counter%2 == 0:
					header_tmp = e.text
				else:
					data[header_tmp] = e.text
				counter +=1
	except:
		print "Error trying to parse additional info for: " + school_url

	return data

def geolocation(address):
	try:
		geocode=gmaps.geocode(address)
	except:
		print "Error gmap for: " + address
		geocode = [{ 'geometry': {'location': {'lat': 0.0, 'lng' :0.0} } }]
	return geocode

def update_data(input_file,output_file,initial_value,end_value):
	try:
		jsoninput = open(input_file)
	except:
		print "Error opening file"
		sys.exit(2)

	data_obj = json.loads(jsoninput.read()) 

	if end_value > len(data_obj):
		end_value = len(data_obj)

	for e in range(initial_value,end_value):
		data_obj[e].update(get_element_data(baseurl+data_obj[e]['Link']))
		try:
			data_obj[e]["geolocation"] = geolocation(data_obj[e]['Address'])[0]['geometry']['location']
		except:
			data_obj[e]["geolocation"] = {'lat': 0.0, 'lng' :0.0}

	jsoninput.close()

	jsonoutput = open(output_file,'w')
	jsonoutput.write(json.JSONEncoder().encode(data_obj[initial_value:end_value]))

if __name__ == "__main__":
	input_file = ''
	output_file = ''
	initial_value = 0
	end_value = 2000
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:s:e:",["ifile=","ofile=","initvalue=","endvalue="])
	except getopt.GetoptError:
		print 'Usage: <script> -i <inputfile> -o <outputfile> -s <initial_value> -e <end_value>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'Usage: <script> -i <inputfile> -o <outputfile> -s <initial_value> -e <end_value>'
			sys.exit()
		elif opt in ("-i","--ifile"):
			input_file = arg
		elif opt in ("-o","--ofile"):
			output_file = arg
		elif opt in ("-s","--initvalue"):
			initial_value = int(arg)
		elif opt in ("-e","--end_value"):
			end_value = int(arg)
	update_data(input_file,output_file,initial_value,end_value)





