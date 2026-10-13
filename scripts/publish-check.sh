#!/usr/bin/env bash
# Content safety gate: fails (exit 1) if any pattern that must never ship
# appears in the repository content. Runs locally and in CI. Fail-closed:
# a hit on any pattern blocks the release until resolved.
set -uo pipefail
cd "$(dirname "$0")/.."

# Everything except VCS internals and the ROOT build output. Exclusions are BY PATH, never by
# basename: --exclude=publish-check.sh or --exclude-dir=dist would also skip skills/x/dist/ or a
# homonym inside skills/, which ships in the zip (review rodadas 6b e 7b). This script itself
# necessarily contains the patterns it greps for: its hits are dropped by path too.
SCAN_ARGS=(-rIEn --exclude-dir=.git)
SELF='./scripts/publish-check.sh:'

PATTERNS=(
  '[0-9]{11}'                                        # CPF-like 11-digit runs
  '\+55[ ().-]*[0-9]{2}[ ().-]*[0-9]{4,5}[ .-]?[0-9]{4}'   # Brazilian phone numbers (with or without separators)
  '[[:alnum:]._%+-]+@(gmail|hotmail|outlook|yahoo|uol|terra)\.'   # personal emails
  'sk-[A-Za-z0-9]{20,}'                              # API-key-like tokens
  'eyJ[A-Za-z0-9_-]{30,}\.'                          # JWT-like tokens
  'AKIA[0-9A-Z]{16}'                                 # AWS access keys
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'               # private key material
)

fail=0
# grep -I pula arquivo "binário" (byte NUL, p.ex. texto salvo em UTF-16) como se não tivesse nada:
# este repo não versiona binário, então arquivo com NUL é conteúdo que a varredura não enxerga ⇒ FAIL
# (review rodada 7b, R1). Fica de fora só o que o package.sh e o .gitignore nunca publicam:
# __pycache__/, *.pyc e .DS_Store (o CI compila antes de testar e gera bytecode na árvore).
while IFS= read -r -d '' f; do
  if ! LC_ALL=C tr -d '\000' < "$f" | cmp -s - "$f"; then
    echo "FAIL: arquivo binário (byte NUL) não pode ser varrido: $f"
    fail=1
  fi
done < <(find . \( -path ./.git -o -path ./dist -o -path ./node_modules -o -name __pycache__ \) -prune \
           -o -type f ! -name '*.pyc' ! -name .DS_Store -print0)
ERR="$(mktemp)"
trap 'rm -f "$ERR"' EXIT
for p in "${PATTERNS[@]}"; do
  # grep: 0 = achou · 1 = não achou · 2 = erro de leitura. Erro NUNCA vira PASS (fail-closed):
  # arquivo ilegível não varrido é exatamente onde o conteúdo proibido passaria.
  hits="$(grep "${SCAN_ARGS[@]}" -- "$p" . 2>"$ERR")"
  rc=$?
  hits="$(printf '%s\n' "$hits" | awk -v s="$SELF" 'length($0) && index($0, s) != 1 && index($0, "./dist/") != 1 && index($0, "./node_modules/") != 1')"
  if [ "$rc" -gt 1 ]; then
    echo "FAIL: varredura incompleta para o padrão $p (grep rc=$rc):"
    head -5 "$ERR"
    fail=1
  fi
  if [ -n "$hits" ]; then
    echo "FAIL: pattern matched: $p"
    echo "$hits" | head -20
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "publish-check: FAIL — resolve the hits above before publishing."
  exit 1
fi
echo "PASS: publish-check found no forbidden content."
