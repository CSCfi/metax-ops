UPDATE metax_api_datacatalog
SET catalog_record_services_create = 'metax,qvain,qvain-light,tpas',
    catalog_record_services_edit = 'metax,qvain,qvain-light,tpas';

UPDATE metax_api_datacatalog
SET catalog_record_services_create = 'metax,tpas',
    catalog_record_services_edit = 'metax,tpas'
WHERE
   catalog_json->>'identifier' LIKE '%-pas';

UPDATE metax_api_datacatalog
SET catalog_record_services_create = 'metax,etsin',
    catalog_record_services_edit = 'metax,etsin'
WHERE
   catalog_json->>'harvested'='true';

