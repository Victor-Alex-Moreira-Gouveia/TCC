#!/bin/bash
mkdir mariadb_data
docker rm tcc-server
docker compose up -d