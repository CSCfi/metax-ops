#!/bin/bash
# Script to reindex all reference data and organization data.
# Run only from the folder where es_index_data.py exists.

source /srv/metax/pyenv/bin/activate
cd /srv/refdata_indexer
python es_index_data.py remove_and_recreate_index=all types_to_reindex=all
