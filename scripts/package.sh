#!/usr/bin/env bash
# Gera um zip por skill em dist/ e o SHA256SUMS.txt dos zips.
# Cada zip tem a pasta da skill na raiz (ex.: spec-make-define/SKILL.md).
# Antes de empacotar, confere que as cópias de compartilhado/ estão em dia (sync --check).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -I scripts/sync-compartilhados.py --check

mkdir -p dist
rm -f dist/*.zip dist/SHA256SUMS.txt

for dir in skills/*/; do
  name="$(basename "$dir")"
  (cd skills && zip -r -q -X "../dist/${name}.zip" "$name" \
    -x "*.DS_Store" -x "*__MACOSX*" -x "*.pyc" -x "*__pycache__*")
  echo "packaged dist/${name}.zip"
done

(cd dist && shasum -a 256 *.zip > SHA256SUMS.txt)
echo "PASS: $(ls dist/*.zip | wc -l | tr -d ' ') skill zips + SHA256SUMS.txt em dist/"
