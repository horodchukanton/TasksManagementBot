#!/usr/bin/env bash
EGGDIR="src/weba_odoo_tasks_management_bot.egg-info"

if [ -d "$EGGDIR" ]; then
    rm -rf ${EGGDIR}
fi

echo 'Building development egg'
pip install -q -e .

echo 'Building done, starting app'
"$@"  # execute command passed to script
