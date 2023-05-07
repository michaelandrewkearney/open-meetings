#!/bin/bash
port=8108

output=$(curl -s http://localhost:${port}/health)

if [ $output == '{"ok":true}' ]; then
  echo true
else 
  echo false
fi