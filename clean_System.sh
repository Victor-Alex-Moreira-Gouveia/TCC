#!/bin/bash
docker compose down -v
docker rmi tcc-server

sudo rm -rdf ./mariadb_data