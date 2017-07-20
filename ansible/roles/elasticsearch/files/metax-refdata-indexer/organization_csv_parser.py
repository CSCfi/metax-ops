'''
	A script that parses csv files and returns a list of organization objects for elasticsearch indexing purposes.

	The first row in a csv file defines the keys that are used to parse the
	organizations. The following keys are accepted as row headers. Separate column values with commas (,):
	year,org_name,org_code,unit_main_code,unit_sub_code,unit_name
	unit_main_code can be left blank, other fields are required.

	This file is a modified version of the original implementation by Peter Kronström.
'''

import csv
import pprint
import json

INPUT_FILES = ['resources/organizations/school_organizations.csv','resources/organizations/research_organizations.csv']
OUTPUT_FILE = '/tmp/metax_organizations.json'

def parse_csv():
	root_orgs = {}
	output_orgs = []

	for csvfile in INPUT_FILES:
		pprint.pprint('Now parsing file {}'.format(csvfile))
		try:
			with open(csvfile, 'r') as csv_file:
				csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
				for row in csv_reader:
					# parse fields in a single row
					org_name = row.get('org_name', '')
					org_code = row.get('org_code', '')
					#unit_main_code = row.get('unit_main_code', '')
					unit_sub_code = row.get('unit_sub_code', '')
					unit_name = row.get('unit_name', '').rstrip()

					if govern(row):
						# save parent ids to parent_organizations dict
						# and create a root level organization
						if not org_code in root_orgs:
							root_org_dict = create_organization(org_code, org_name)
							root_orgs[org_code] = root_org_dict.get('org_id', None)
							output_orgs.append(root_org_dict)

						# otherwise create an org and append it to existing root's hierarchy
						if unit_sub_code and unit_name:
							organization_code = '-'.join([org_code, unit_sub_code])		# Unique
							parent_id = root_orgs.get(org_code, None)
							output_orgs.append(create_organization(organization_code, unit_name, parent_name=org_name, parent_id=parent_id))

		except IOError:
			pprint.pprint('File {} could not be found.'.format(csvfile))

	with open(OUTPUT_FILE, 'w+') as outfile:
		json.dump(output_orgs, outfile)


def govern(row):
	'''
		returns false, if the row does not contain necessary fields.
	'''

	# root-level organization only
	if all(row[i] for i in ['org_name', 'org_code']):
		# check if sub-unit fields are present
		if not all(row[i] for i in ['unit_sub_code', 'unit_name']):
			print('Missing unit codes (unit_sub_code, unit_name). Creating root organization only: {}'.format(row))
		return True
	else:
		print('Missing root organization fields (org_name, org_code). Skipping row {}'.format(row))
		return False


def create_organization(org_id_str, org_name, parent_name=None, parent_id=None):
	'''
		create organization data_dict that is suitable for ES indexing
	'''
	org_dict = {}
	org_dict['org_id'] = org_id_str
	org_dict['label'] = {'fi': org_name, 'default': org_name}

	if parent_id and parent_name:
		org_dict['broader_id'] = parent_id
		org_dict['broader_label'] = parent_name

	return org_dict
