#!/bin/bash
# Script to reindex all reference data and organization data.
# Run only from the folder where es_index_data.py exists.

cd /usr/local/metax/refdata_indexer
source /usr/local/metax/pyenv/bin/activate

if [ "$USER" != "metax-user" ]; then
    echo "Run this as metax-user"
    exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Give exactly one parameter to the script. Either 'delete_and_reindex' or 'only_reindex'"
  exit 2
fi

if [ "$1" != "delete_and_reindex" ] && [ "$1" != "only_reindex" ]; then
  echo "Give exactly one parameter to the script. Either 'delete_and_reindex' or 'only_reindex'"
  exit 3
fi

if [ "$1" == "delete_and_reindex" ]; then
  PARAM="all"
fi

if [ "$1" == "only_reindex" ]; then
    PARAM="no"
fi

source /usr/local/metax/pyenv/bin/activate
cd /usr/local/metax/refdata_indexer
python index_data.py remove_and_recreate_index=$PARAM types_to_reindex=all
