#!/bin/bash
docker compose down -v 
sudo rm -rdf ./mariadb_data
docker rmi tcc-server

mkdir mariadb_data
docker compose up -d