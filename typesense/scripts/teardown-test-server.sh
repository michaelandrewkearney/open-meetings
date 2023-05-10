#!/bin/bash
docker stop opm-test
docker rm opm-test
docker volume rm typesense-test-db