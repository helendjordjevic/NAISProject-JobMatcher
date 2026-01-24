#!/bin/bash

# Kreiranje indeksa
curl -X PUT "localhost:9200/candidates" -H 'Content-Type: application/json' -d @mappings/candidates_mapping.json
curl -X PUT "localhost:9200/jobads" -H 'Content-Type: application/json' -d @mappings/jobads_mapping.json

# Ubacivanje sample podataka
for row in $(cat sample_data/candidates_sample.json | jq -c '.[]'); do
  curl -X POST "localhost:9200/candidates/_doc" -H 'Content-Type: application/json' -d "$row"
done

for row in $(cat sample_data/jobads_sample.json | jq -c '.[]'); do
  curl -X POST "localhost:9200/jobads/_doc" -H 'Content-Type: application/json' -d "$row"
done
