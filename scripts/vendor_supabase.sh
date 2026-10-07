#!/usr/bin/env bash
# trim vendored supabase-js to the standalone browser bundle + license
set -euo pipefail
cd /opt/data/learning-app/public/vendor
if [ -d supabase-js ]; then
  mv supabase-js/dist/umd/supabase.js ./supabase.umd.js
  mv supabase-js/LICENSE ./supabase.LICENSE
  rm -rf supabase-js
fi
ls -la
