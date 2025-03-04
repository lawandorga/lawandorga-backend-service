#!/usr/bin/env bash

find ./core -name '*.py' \
  -type f \
  -not -path '*/migrations/*' \
  -not -path '*/tests/*' \
  -not -iname '*test*.py' \
| while read file; do
  line_count="$(wc -l < "$file")"
  if [ "$line_count" -gt 300 ]; then
    echo "$file - ${line_count} lines"
  fi
done