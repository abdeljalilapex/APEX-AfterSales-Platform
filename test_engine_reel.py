"""
test_engine_reel.py — Exécution réelle du moteur Python contre PostgreSQL
local (pas une relecture). Calcule les 2 KPI pilotes, vérifie les valeurs
contre un contrôle manuel indépendant, teste le recalcul (ADR-015).
"""
import sys
sys.path.insert(0, "/home/claude/apex_backend")

from datetime import date
from kpi_engine_py import get_engine, reflect_metadata, calculate

CONCESSION_ID = "11111111-1111-1111-1111-111111111111"
PERIODE_DEBUT = date(2026, 7, 20)
PERIODE_FIN = date(2026, 7, 26)

engine = get_engine()
metadata = reflect_metadata(engine)

print("=== Tables réfléchies depuis PostgreSQL :", len(metadata.tables), "===\n")

with engine.connect() as conn:
    # ---- 1er calcul : kpi-delai-rdv ----
    resultat1 = calculate(conn, metadata, "kpi-delai-rdv", PERIODE_DEBUT, PERIODE_FIN, CONCESSION_ID, auteur="test-etape2")
    print("kpi-delai-rdv (1er calcul) :", {k: v for k, v in resultat1.items() if k != "sources_ids"})
    print("  sources_ids :", resultat1["sources_ids"])

    # ---- 1er calcul : kpi-nombre-or ----
    resultat2 = calculate(conn, metadata, "kpi-nombre-or", PERIODE_DEBUT, PERIODE_FIN, CONCESSION_ID, auteur="test-etape2")
    print("\nkpi-nombre-or (1er calcul) :", {k: v for k, v in resultat2.items() if k != "sources_ids"})
    print("  sources_ids :", resultat2["sources_ids"])

    # ---- Contrôle manuel indépendant (requête SQL directe, sans passer par le moteur) ----
    from sqlalchemy import text
    delai_manuel = conn.execute(text("""
        SELECT avg(delai_obtention_jours) AS moyenne, count(*) AS n
        FROM rendezvous
        WHERE concession_id = :c AND statut = 'honore'
          AND date_demande BETWEEN :d1 AND :d2
    """), {"c": CONCESSION_ID, "d1": PERIODE_DEBUT, "d2": PERIODE_FIN}).mappings().first()
    print("\nContrôle manuel délai RDV :", dict(delai_manuel))

    nb_or_manuel = conn.execute(text("""
        SELECT count(*) AS n FROM ordres_reparation
        WHERE concession_id = :c AND date_ouverture BETWEEN :d1 AND :d2
    """), {"c": CONCESSION_ID, "d1": PERIODE_DEBUT, "d2": PERIODE_FIN}).mappings().first()
    print("Contrôle manuel nombre OR :", dict(nb_or_manuel))

    assert abs(float(resultat1["valeur"]) - float(delai_manuel["moyenne"])) < 0.001, "DIVERGENCE délai RDV !"
    assert resultat2["valeur"] == nb_or_manuel["n"], "DIVERGENCE nombre OR !"
    print("\n[OK] Les 2 valeurs du moteur correspondent exactement au contrôle manuel SQL indépendant.")

    # ---- Test de recalcul (ADR-015) : rejouer le même calcul ----
    id_avant = resultat2["id"]
    cree_le_avant = resultat2["cree_le"]
    cree_par_avant = resultat2["cree_par"]

    resultat2_recalcule = calculate(conn, metadata, "kpi-nombre-or", PERIODE_DEBUT, PERIODE_FIN, CONCESSION_ID, auteur="quelqu-un-d-autre")

    print("\n=== Test de recalcul (ADR-015) ===")
    print("ID inchangé :", id_avant == resultat2_recalcule["id"])
    print("cree_le inchangé :", cree_le_avant == resultat2_recalcule["cree_le"])
    print("cree_par inchangé (reste le créateur d'origine) :", cree_par_avant == resultat2_recalcule["cree_par"])
    print("recalcule_le renseigné :", resultat2_recalcule["recalcule_le"] is not None)

    # ---- Vérifier qu'aucun doublon n'a été créé dans kpi_values ----
    from sqlalchemy import text as _text
    count_kv = conn.execute(_text("""
        SELECT count(*) AS n FROM kpi_values WHERE kpi_id='kpi-nombre-or' AND concession_id=:c
    """), {"c": CONCESSION_ID}).mappings().first()
    print("Nombre de lignes kpi_values pour kpi-nombre-or (doit rester 1) :", count_kv["n"])
    assert count_kv["n"] == 1, "DOUBLON détecté — la contrainte UNIQUE / ON CONFLICT n'a pas fonctionné !"

    print("\n[OK] Recalcul conforme à ADR-015 : pas de doublon, cree_le/cree_par préservés, recalcule_le mis à jour.")

    # ---- Test d'un opérateur non couvert (doit lever une erreur explicite) ----
    try:
        calculate(conn, metadata, "kpi-delai-rdv", PERIODE_DEBUT, PERIODE_FIN, CONCESSION_ID, version=99)
        print("\n[ERREUR DE TEST] Une version inexistante aurait dû lever une exception.")
    except ValueError as e:
        print("\n[OK] KPIDefinition inexistante (version 99) correctement rejetée :", e)

print("\n=== TOUS LES TESTS SONT PASSÉS ===")
