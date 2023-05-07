#!/bin/bash
output=$(curl -s http://localhost:8108/health)

if [ $output == '{"ok":true}' ]; then
  echo true
else 
  echo false
fi