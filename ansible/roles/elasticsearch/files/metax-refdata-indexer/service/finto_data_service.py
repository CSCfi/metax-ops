import json
import requests
import xml.etree.cElementTree as ET
import os
from domain.reference_data import ReferenceData
import rdflib
from rdflib import URIRef

class FintoDataService:
    '''
    Service for getting reference data for elasticsearch index. The data is in Finto,
    so it is first fetched and parsed.
    '''


    SKOS_NS = '{http://www.w3.org/2004/02/skos/core#}'
    RDF_NS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
    XML_NS = '{http://www.w3.org/XML/1998/namespace}'
    LVONT_NS = '{http://lexvo.org/ontology#}'

    FINTO_REFERENCE_DATA_SOURCE_URLS = {
        ReferenceData.DATA_TYPE_FIELD_OF_SCIENCE: 'http://finto.fi/rest/v1/okm-tieteenala/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_LANGUAGE: 'http://finto.fi/rest/v1/lexvo/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_LOCATION: 'http://finto.fi/rest/v1/yso-paikat/data?format=application/rdf%2Bxml',
        ReferenceData.DATA_TYPE_KEYWORD: 'http://finto.fi/rest/v1/yso/data?format=application/rdf%2Bxml'
    }

    FINTO_MODEL_ELEM = {
        ReferenceData.DATA_TYPE_FIELD_OF_SCIENCE: SKOS_NS + 'Concept',
        ReferenceData.DATA_TYPE_LANGUAGE: LVONT_NS + 'Language',
        ReferenceData.DATA_TYPE_LOCATION: SKOS_NS + 'Concept',
        ReferenceData.DATA_TYPE_KEYWORD: SKOS_NS + 'Concept'
    }

    TEMP_XML_FILENAME = '/tmp/data.xml'

    WKT_FILENAME = './resources/uri_to_wkt.json'

    # Use this to decide whether to read location coordinates from a file
    # or whether to read coordinates from wikidata and paikkatiedot.fi and
    # at the same time writing the coordinates to a file
    READ_COORDINATES_FROM_FILE = True

    def get_data(self, data_type):
        self._fetch_finto_data(data_type)
        index_data_models = self._parse_finto_data(data_type)
        os.remove(self.TEMP_XML_FILENAME)
        return index_data_models

    def _parse_finto_data(self, data_type):
        index_data_models = []
        model_elem = self.FINTO_MODEL_ELEM[data_type]

        print("Extracting relevant data from the fetched data")
        is_parsing_model_elem = False

        if self.READ_COORDINATES_FROM_FILE:
            with open(self.WKT_FILENAME) as c:
                coordinates = json.load(c)
        else:
            with open(self.WKT_FILENAME, 'w') as outfile:
                outfile.write('{\n')

        for event, elem in ET.iterparse(self.TEMP_XML_FILENAME, events=("start", "end")):
            if event == 'start':
                if elem.tag == model_elem:
                    is_parsing_model_elem = True
                    uri = elem.attrib[self.RDF_NS + 'about']
                    label = {}
                    parent_ids = []
                    child_ids = []
                    same_as = []
                    wkt = ''
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'prefLabel':
                    if elem.text:
                        label[elem.attrib[self.XML_NS + 'lang']] = elem.text
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'broader':
                    parent_ids.append(self._get_uri_end_part(elem.attrib[self.RDF_NS + 'resource']))
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'narrower':
                    child_ids.append(self._get_uri_end_part(elem.attrib[self.RDF_NS + 'resource']))
                if is_parsing_model_elem and elem.tag == self.SKOS_NS + 'closeMatch' and not len(wkt):
                    if self.READ_COORDINATES_FROM_FILE:
                        wkt = coordinates.get(uri, '')
                    else:
                        wkt = self._get_coordinates_for_location_from_url(elem.attrib[self.RDF_NS + 'resource'])
                        with open(self.WKT_FILENAME, 'a') as outfile:
                            outfile.write("\"" + uri + "\":\"" + wkt + '\",\n')
            elif event == 'end' and elem.tag == model_elem:
                is_parsing_model_elem = False
                data_id = self._get_uri_end_part(uri)
                index_data_models.append(ReferenceData(data_id,
                                                        data_type,
                                                        label,
                                                        uri,
                                                        parent_ids,
                                                        child_ids,
                                                        same_as,
                                                        wkt))

        if not self.READ_COORDINATES_FROM_FILE:
            with open(self.WKT_FILENAME, 'a') as outfile:
                outfile.write('}')
        print("Done with all")
        return index_data_models

    def _fetch_finto_data(self, data_type):
        url = self.FINTO_REFERENCE_DATA_SOURCE_URLS[data_type]
        print("Fetching data from url " + url)
        response = requests.get(url, stream=True)
        with open(self.TEMP_XML_FILENAME, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)


    def _get_uri_end_part(self, uri):
        return uri[uri.rindex('/')+1:].strip()

    def _get_coordinates_for_location_from_url(self, url):
        output = ''
        if 'wikidata' in url:
           g=rdflib.Graph()
           try:
               g.parse(url + '.rdf')
               subject = URIRef(url)
               predicate = URIRef('http://www.wikidata.org/prop/direct/P625')
               for o in g.objects(subject, predicate):
                   return str(o).upper()
           except:
               print("Unable to read wikidata, skipping..")

        elif 'paikkatiedot' in url:
            response = requests.get(url +'.jsonld')
            if response.status_code == requests.codes.ok:
                data_as_str = self._find_between(response.text, '<script type="application/ld+json">', '</script>')
                if data_as_str:
                    data = json.loads(data_as_str)
                    if data and data.get('geo', False) and data.get('geo').get('latitude', False) and data.get('geo').get('longitude', False):
                        output = 'POINT(' + str(data['geo']['longitude']) + ' ' + str(data['geo']['latitude']) + ')'

        return output

    def _find_between(self, s, first, last):
        try:
            if s:
                start = s.index(first) + len(first)
                end = s.index(last, start)
                return s[start:end]
        except Exception:
            pass
        return None
