#!/bin/bash
output=$(curl http://localhost:8108/health | grep '{"ok":true}')
echo $output