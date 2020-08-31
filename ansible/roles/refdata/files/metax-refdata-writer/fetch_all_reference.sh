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
  echo "Give exactly one parameter to the script: path to the reference data repository."
  exit 2
fi

if [ ! -d "$1" ]; then
  echo "Directory $1 DOES NOT exists."
  exit 3
fi

REPO_PATH=$1

source /usr/local/metax/pyenv/bin/activate
cd /usr/local/metax/refdata_writer
python fetch_data.py $REPO_PATH