#!/bin/bash
HOST=$1
DB=$2

if [ -z "${HOST}" ] || [ -z "${DB}" ]; then
    echo "Usage: $0 <db host> <db name>"
    exit 1
fi

echo "Running Pre-init SQL"
psql -h ${HOST} ${DB} < migrate-preinit.sql

if [ $? -ne 0 ]; then
    echo "Error during pre-init"
    exit 2
fi

echo "Running pylol-init"
pylol-init

if [ $? -ne 0 ]; then
    echo "Error during init"
    exit 3
fi

echo "Running Post-init SQL"
psql -h ${HOST} ${DB} < migrate-postinit.sql

if [ $? -ne 0 ]; then
    echo "Error during Pre-init"
    exit 2
fi

