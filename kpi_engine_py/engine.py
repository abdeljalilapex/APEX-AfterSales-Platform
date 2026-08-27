"""
engine.py — Interface d'exécution unique du KPI Engine (port Python).

Respecte le principe 3bis (ADR-008) : cette fonction ne sait jamais qui
l'appelle (script manuel ici, Scheduler ou API plus tard). Elle ne fait
que : lire la définition -> extraire -> calculer -> évaluer -> écrire.
"""

from sqlalchemy import select

from .extracteur import extraire_donnees
from .calculateur import calculer_agregation
from .evaluateur import evaluer_statut
from .ecrivain import ecrire_resultat


def _charger_definition(conn, metadata, kpi_id: str, version: int = None) -> dict:
    kpi_definitions = metadata.tables["kpi_definitions"]
    stmt = select(kpi_definitions).where(kpi_definitions.c.id == kpi_id)
    if version is not None:
        stmt = stmt.where(kpi_definitions.c.version == version)
    else:
        stmt = stmt.order_by(kpi_definitions.c.version.desc())
    row = conn.execute(stmt).mappings().first()
    if row is None:
        raise ValueError(f"KPI Engine — KPIDefinition introuvable : {kpi_id}")
    return dict(row)


def calculate(conn, metadata, kpi_id: str, periode_debut, periode_fin, concession_id,
              version: int = None, auteur: str = "system") -> dict:
    """
    Point d'entrée unique du moteur. Signature volontairement proche de
    KPIEngine.calculate() côté JavaScript, pour que la fidélité du portage
    reste vérifiable à l'œil.
    """
    definition = _charger_definition(conn, metadata, kpi_id, version)

    data = extraire_donnees(conn, metadata, definition, periode_debut, periode_fin, concession_id)

    agregation = {
        "type": definition["agregation_type"],
        "champ": definition["agregation_champ"],
    }
    valeur = calculer_agregation(agregation, data)
    statut = evaluer_statut(valeur, definition)
    sources_ids = [r["id"] for r in data]

    resultat = {
        "kpi_id": definition["id"],
        "version": definition["version"],
        "periode_debut": periode_debut,
        "periode_fin": periode_fin,
        "concession_id": concession_id,
        "valeur": valeur,
        "statut": statut,
    }
    return ecrire_resultat(conn, metadata, resultat, sources_ids, auteur)
