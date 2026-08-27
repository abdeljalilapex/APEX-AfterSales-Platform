"""
test_api_reel_supabase.py — Exécution réelle de l'API FastAPI (TestClient)
contre Supabase réel : vraie base (DATABASE_URL), vrai JWKS Supabase
(SUPABASE_URL depuis .env, non modifié), et vrai token obtenu par login
réel (/tmp/test_token.txt) — pas de génération locale de token.
"""
import sys, os
sys.path.insert(0, ".")

# IMPORTANT : ne PAS toucher à SUPABASE_URL ici — on garde celui de .env
# (le vrai projet Supabase), chargé par `source .env` avant ce script.
assert os.environ.get("SUPABASE_URL", "").startswith("https://"), \
    "SUPABASE_URL doit pointer vers le vrai projet Supabase (as-tu bien fait `source .env` ?)"

with open("/tmp/test_token.txt") as f:
    TOKEN = f.read().strip()

from fastapi.testclient import TestClient
from api.main import app

CONCESSION_ID = "11111111-1111-1111-1111-111111111111"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

with TestClient(app) as client:
    r = client.get("/health")
    print("GET /health ->", r.status_code, r.json())
    assert r.status_code == 200

    r = client.get("/kpi-definitions")
    print("\nGET /kpi-definitions (sans token) ->", r.status_code, r.json())
    assert r.status_code == 401

    r = client.get("/kpi-definitions", headers={"Authorization": "Bearer invalide"})
    print("GET /kpi-definitions (token invalide) ->", r.status_code, r.json())
    assert r.status_code == 401

    r = client.get("/kpi-definitions", headers=HEADERS)
    print("\nGET /kpi-definitions (token réel Supabase) ->", r.status_code, "-", len(r.json()), "définitions")
    assert r.status_code == 200

    r = client.post("/kpi/kpi-delai-rdv/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": CONCESSION_ID,
    })
    print("\nPOST /kpi/kpi-delai-rdv/calculer ->", r.status_code)
    print("  ", r.json())
    assert r.status_code == 200, f"Échec inattendu : {r.json()}"
    v1 = r.json()
    assert v1["cree_par"] is not None

    r = client.post("/kpi/kpi-delai-rdv/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": "99999999-0000-0000-0000-000000000000",
    })
    print("\nPOST /kpi/.../calculer (concession hors organisation) ->", r.status_code, r.json())
    assert r.status_code == 403

    r = client.post("/kpi/kpi-nombre-or/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": CONCESSION_ID,
    })
    v2 = r.json()
    print("\nPOST /kpi/kpi-nombre-or/calculer ->", r.status_code, v2)
    assert r.status_code == 200
    # cree_par doit venir du vrai user_id du token (sub), ou rester la valeur
    # d'un run précédent si c'est un recalcul (ADR-015) — les deux sont valides.
    print("   cree_par =", v2.get("cree_par"))

    r = client.get(f"/kpi/kpi-nombre-or/valeurs?concession_id={CONCESSION_ID}", headers=HEADERS)
    print("\nGET /kpi/kpi-nombre-or/valeurs ->", r.status_code, "-", len(r.json()), "valeur(s)")
    assert r.status_code == 200

    value_id = v2["id"]
    r = client.get(f"/kpi-values/{value_id}/sources", headers=HEADERS)
    print("\nGET /kpi-values/{id}/sources ->", r.status_code, "-", len(r.json()), "enregistrement(s) source")
    assert r.status_code == 200

    r = client.post("/kpi/kpi-inexistant/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26", "concession_id": CONCESSION_ID,
    })
    print("\nPOST /kpi/kpi-inexistant/calculer ->", r.status_code, "-", r.json())
    assert r.status_code == 404

    r = client.get("/kpi-values/00000000-0000-0000-0000-000000000000/sources", headers=HEADERS)
    print("GET /kpi-values/{id-inexistant}/sources ->", r.status_code, "-", r.json())
    assert r.status_code == 404

print("\n=== TOUS LES TESTS PASSÉS CONTRE SUPABASE RÉEL (base + JWKS + token réels) ===")
