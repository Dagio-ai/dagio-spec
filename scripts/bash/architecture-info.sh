#!/usr/bin/env bash
set -euo pipefail

arch_dir="${ARCHITECTURE_DIR:-specs/architecture}"
readme_path="$arch_dir/README.md"
overview_path="$arch_dir/architecture_overview.md"
architecture_json="$arch_dir/architecture.json"
log_path="$arch_dir/architecture_logs.md"

# Default expectations when no JSON model exists yet
fallback_views=(
  "architecture_overview.md"
  "architecture_logs.md"
  "c1_context/system_context.md"
  "c2_containers/containers_overview.md"
  "c5_dynamic_view/view_diagram.md"
  "c6_deployment/deployment_diagram.md"
  "c7_tests/tests_overview.md"
)

mkdir -p "$arch_dir"

get_expected_views() {
  if [ -f "$architecture_json" ]; then
    python - <<'PY' "$architecture_json"
import json
import sys
from pathlib import Path

FALLBACK = [
    "architecture_overview.md",
    "architecture_logs.md",
    "c1_context/system_context.md",
    "c2_containers/containers_overview.md",
    "c5_dynamic_view/view_diagram.md",
    "c6_deployment/deployment_diagram.md",
    "c7_tests/tests_overview.md",
]

def normalise(path: str) -> str:
    if not path:
        return ""
    path = path.replace('\\', '/').strip()
    prefix = "specs/architecture/"
    if path.startswith(prefix):
        return path[len(prefix):]
    return path

try:
    data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    views = []
    raw_views = data.get('views', {})
    if isinstance(raw_views, dict):
        for entry in raw_views.values():
            if isinstance(entry, dict):
                norm = normalise(entry.get('path'))
                if norm:
                    views.append(norm)
    if not views:
        views = FALLBACK
except Exception:
    views = FALLBACK

for item in views:
    print(item)
PY
  else
    printf '%s
' "${fallback_views[@]}"
  fi
}

mapfile -t expected_views < <(get_expected_views)

existing_views=()
missing_views=()
for view in "${expected_views[@]}"; do
  candidate="$arch_dir/$view"
  if [ -f "$candidate" ]; then
    existing_views+=("$view")
  else
    missing_views+=("$view")
  fi
done

print_array() {
  local items=("$@")
  local first=true
  printf '['
  for item in "${items[@]}"; do
    if [ "$first" = false ]; then
      printf ', '
    fi
    printf '"%s"' "$item"
    first=false
  done
  printf ']'
}

model_version_json="null"
if [ -f "$architecture_json" ]; then
  model_version_json=$(python - <<'PY' "$architecture_json"
import json
import sys
from pathlib import Path

def main(path: str) -> None:
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        value = data.get('model_version')
    except Exception:
        value = None
    import json as _json
    print(_json.dumps(value))

if __name__ == '__main__':
    main(sys.argv[1])
PY
  )
fi

echo '{'
echo "  \"architecture_dir\": \"$arch_dir\","
echo "  \"readme\": \"$readme_path\","
echo "  \"overview\": \"$overview_path\","
echo "  \"architecture_json\": \"$architecture_json\","
echo "  \"architecture_log\": \"$log_path\","
echo "  \"model_version\": $model_version_json,"
printf '  "expected_views": ' ; print_array "${expected_views[@]}" ; echo ','
printf '  "existing_views": ' ; print_array "${existing_views[@]}" ; echo ','
printf '  "missing_views": ' ; print_array "${missing_views[@]}"
echo '}'
