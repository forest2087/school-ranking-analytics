from elasticsearch import Elasticsearch
import os, sys, getopt, json

# Init Elasticsearch
es = Elasticsearch([os.getenv('ES_URL','http://localhost:9200')])
data_index = "ontario-schools-rank"
data_type = "elementary-school"

def inject_data(json_file, data_id):
	if not os.path.isfile(json_file):
		print "File:" + json_file + "doesn't exist"
		sys.exit(2)

	try:
		file = open(json_file, 'r')
		json_array = json.loads(file.read())
	except:
		print "Error loading json file"
		sys.exit(2)

	for element in json_array:
		print "inserting: " + str(element)
		result = es.index( index = data_index, doc_type = data_type, id = data_id, body = element)
		print(result['created'])
		data_id += 1


if __name__ == "__main__":
	json_file = ''
	data_id = 100001
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hf:i:",["file=","id="])
	except getopt.GetoptError:
		print "Usage: <script> -f <json_file> [-i <initial_id>]"
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print "Usage: <script> -f <json_file> [-i <initial_id>]"
			sys.exit()
		elif opt in ("-f","--file"):
			json_file = arg
		elif opt in ("-i","--id"):
			data_id = int(arg)
	inject_data(json_file,data_id)



