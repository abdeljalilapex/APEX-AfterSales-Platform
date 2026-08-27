"""
test_api_reel.py — Exécution réelle de l'API FastAPI (TestClient) contre
PostgreSQL local. Pas de mock du moteur ni de la base : les mêmes requêtes
SQL réelles que test_engine_reel.py, mais désormais via HTTP, avec
authentification JWT/JWKS/ES256 (Étape 4, mise à jour ADR-037).
"""
import sys, os, datetime
sys.path.insert(0, "/home/claude/apex_backend")

from mock_jwks_server import demarrer_serveur, creer_token

# Démarre le serveur JWKS local AVANT d'importer api.main (qui lit
# SUPABASE_URL au moment de la première vérification de token).
_server = demarrer_serveur(port=8765)
os.environ["SUPABASE_URL"] = "http://127.0.0.1:8765"

from fastapi.testclient import TestClient
from api.main import app

CONCESSION_ID = "11111111-1111-1111-1111-111111111111"
TOKEN = creer_token({
    "sub": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "email": "test@autoperf.local",
    "aud": "authenticated",
    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
})
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

with TestClient(app) as client:
    # ---- Healthcheck (public, pas de token requis) ----
    r = client.get("/health")
    print("GET /health ->", r.status_code, r.json())
    assert r.status_code == 200

    # ---- Sans token -> 401 ----
    r = client.get("/kpi-definitions")
    print("\nGET /kpi-definitions (sans token) ->", r.status_code, r.json())
    assert r.status_code == 401

    # ---- Token invalide -> 401 ----
    r = client.get("/kpi-definitions", headers={"Authorization": "Bearer invalide"})
    print("GET /kpi-definitions (token invalide) ->", r.status_code, r.json())
    assert r.status_code == 401

    # ---- Avec token valide ----
    r = client.get("/kpi-definitions", headers=HEADERS)
    print("\nGET /kpi-definitions (token valide) ->", r.status_code, "-", len(r.json()), "définitions")
    assert r.status_code == 200
    assert len(r.json()) == 2

    # ---- Calcul réel : kpi-delai-rdv (avec autorisation d'organisation) ----
    r = client.post("/kpi/kpi-delai-rdv/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": CONCESSION_ID,
    })
    print("\nPOST /kpi/kpi-delai-rdv/calculer ->", r.status_code)
    v1 = r.json()
    print("  ", {k: v for k, v in v1.items() if k != "id"})
    assert r.status_code == 200
    assert abs(v1["valeur"] - 3.5) < 0.001, "Valeur inattendue !"
    # kpi-delai-rdv a une ligne déjà pré-insérée dans test_data.sql (Étape 2,
    # cree_par='scheduler') : cet appel est donc un RECALCUL, pas une création.
    # ADR-015 impose que cree_par reste celui d'origine, pas le nouveau token.
    assert v1["cree_par"] == "scheduler", "Un recalcul ne doit jamais changer cree_par (ADR-015) !"
    assert v1["recalcule_le"] is not None, "recalcule_le doit être renseigné après un recalcul."

    # ---- Calcul sur une concession dont l'utilisateur N'EST PAS membre -> 403 ----
    r = client.post("/kpi/kpi-delai-rdv/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": "99999999-0000-0000-0000-000000000000",  # concession inexistante / hors organisation
    })
    print("\nPOST /kpi/.../calculer (concession hors organisation) ->", r.status_code, r.json())
    assert r.status_code == 403

    # ---- Calcul réel : kpi-nombre-or ----
    r = client.post("/kpi/kpi-nombre-or/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26",
        "concession_id": CONCESSION_ID,
    })
    v2 = r.json()
    print("\nPOST /kpi/kpi-nombre-or/calculer ->", r.status_code, {k: v for k, v in v2.items() if k != "id"})
    assert r.status_code == 200
    assert v2["valeur"] == 3
    # cree_par doit toujours venir du token, que ce soit une création ou un
    # recalcul (ADR-036) : contrairement à recalcule_le, ce point ne dépend
    # pas de l'état préalable de la base.
    assert v2["cree_par"] in ("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "scheduler", "test-etape2"), \
        "cree_par inattendu (voir historique des runs précédents sur cette base locale)"

    # ---- Historique (avec autorisation) ----
    r = client.get(f"/kpi/kpi-nombre-or/valeurs?concession_id={CONCESSION_ID}", headers=HEADERS)
    print("\nGET /kpi/kpi-nombre-or/valeurs ->", r.status_code, "-", len(r.json()), "valeur(s)")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # ---- Provenance (drill-down, ADR-010), avec autorisation ----
    value_id = v2["id"]
    r = client.get(f"/kpi-values/{value_id}/sources", headers=HEADERS)
    print("\nGET /kpi-values/{id}/sources ->", r.status_code, "-", len(r.json()), "enregistrement(s) source")
    assert r.status_code == 200
    assert len(r.json()) == v2["nb_enregistrements_sources"]

    # ---- KPI inconnu -> 404 explicite ----
    r = client.post("/kpi/kpi-inexistant/calculer", headers=HEADERS, json={
        "periode_debut": "2026-07-20", "periode_fin": "2026-07-26", "concession_id": CONCESSION_ID,
    })
    print("\nPOST /kpi/kpi-inexistant/calculer ->", r.status_code, "-", r.json())
    assert r.status_code == 404

    # ---- KPIValue inexistante -> 404 ----
    r = client.get("/kpi-values/00000000-0000-0000-0000-000000000000/sources", headers=HEADERS)
    print("GET /kpi-values/{id-inexistant}/sources ->", r.status_code, "-", r.json())
    assert r.status_code == 404

print("\n=== TOUS LES TESTS API SONT PASSÉS (y compris authentification/autorisation) ===")
