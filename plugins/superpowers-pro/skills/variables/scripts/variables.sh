#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: variables.sh show <variables-json-path>" >&2
  echo "       variables.sh set <variables-json-path> <name> <value>" >&2
  exit 1
}

[ $# -lt 2 ] && usage

ACTION="$1"
VARS_FILE="$2"

if [ ! -f "$VARS_FILE" ]; then
  echo "ERROR: variables file not found: $VARS_FILE" >&2
  exit 1
fi

case "$ACTION" in
  show)
    python3 -c "
import json, sys
data = json.load(open('$VARS_FILE'))
for key, val in data.items():
    opts = ', '.join(val['values'])
    print(f\"{key}: {val['default']} (可选: {opts}) — {val['description']}\")
"
    ;;

  set)
    [ $# -lt 4 ] && usage
    VAR_NAME="$3"
    VAR_VALUE="$4"

    python3 -c "
import json, sys

path = '$VARS_FILE'
name = '$VAR_NAME'
value = '$VAR_VALUE'

with open(path) as f:
    data = json.load(f)

if name not in data:
    available = ', '.join(data.keys())
    print(f'ERROR: unknown variable \"{name}\". Available: {available}', file=sys.stderr)
    sys.exit(1)

if value not in data[name]['values']:
    valid = ', '.join(data[name]['values'])
    print(f'ERROR: invalid value \"{value}\" for {name}. Valid values: {valid}', file=sys.stderr)
    sys.exit(1)

data[name]['default'] = value
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'OK: {name} = {value}')
"
    ;;

  *)
    usage
    ;;
esac
