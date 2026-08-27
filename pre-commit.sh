#!/bin/bash
# Pre-commit hook — APEX AutoPerf Group
# Bloque tout commit contenant un motif ressemblant à une clé/secret Supabase
# ou à un mot de passe en clair dans une chaîne de connexion.
#
# Installation (à faire une seule fois dans Codespaces) :
#   cp pre-commit .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

set -e

# Motifs à bloquer :
#   eyJ        -> début typique d'un JWT (anon key / service_role key Supabase)
#   sbp_       -> préfixe des tokens d'accès personnels Supabase
#   postgresql://postgres.*:.*@   -> connection string avec mot de passe en clair
PATTERNS='eyJ|sbp_|postgresql(\+psycopg2)?://[^ ]*:[^ ]*@'

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

FOUND=0
for FILE in $STAGED_FILES; do
    if [ -f "$FILE" ]; then
        MATCHES=$(grep -nE "$PATTERNS" "$FILE" || true)
        if [ -n "$MATCHES" ]; then
            echo "🚫 Secret potentiel détecté dans : $FILE"
            echo "$MATCHES"
            echo ""
            FOUND=1
        fi
    fi
done

if [ "$FOUND" -eq 1 ]; then
    echo "Commit bloqué : retire le secret ou la chaîne de connexion en clair avant de committer."
    echo "Si c'est un faux positif, utilise : git commit --no-verify (à n'utiliser qu'en connaissance de cause)."
    exit 1
fi

exit 0
