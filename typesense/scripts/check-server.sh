#!/bin/bash
port=$1

output=$(curl -s http://localhost:${port}/health)

if [ $output == '{"ok":true}' ]; then
  echo true
else 
  echo false
fi