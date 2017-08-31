import json
import os
from organization_csv_parser import OUTPUT_FILE as PARSER_OUTPUT_FILE_PATH
from domain.organization_data import OrganizationData
import organization_csv_parser as org_parser

class OrganizationService:
    '''
    Service for getting organization data for elasticsearch index
    '''

    INPUT_FILE = PARSER_OUTPUT_FILE_PATH

    def get_data(self):
        # Parse csv files containing organizational data
        org_parser.parse_csv()

        index_data_models = []
        with open(self.INPUT_FILE) as org_data_file:
            data = json.load(org_data_file)

        for org in data:
            parent_id = org.get('parent_id', '')
            parent_label = org.get('parent_label', '')
            same_as = org.get('same_as', [])
            org_csc = org.get('org_csc', '')
            index_data_models.append(OrganizationData(org['org_id'], org['label'], parent_id, parent_label, same_as, org_csc))

        # if len(index_data_models) > 0:
        #     for ref in index_data_models:
        #         print(ref, sep='\n\n')

        os.remove(self.INPUT_FILE)
        return index_data_models
