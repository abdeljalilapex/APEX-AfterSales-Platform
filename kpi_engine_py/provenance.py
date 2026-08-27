"""
provenance.py — Résout les sources_ids d'une KPIValue vers les enregistrements
réels (ADR-010 : drill-down jusqu'aux identifiants exacts).

Extension minimale du module kpi_engine_py, ajoutée pour l'Étape 3 (API) :
la persistance des sources_ids existait déjà depuis KPI-2/ecrivain.py, mais
aucune fonction ne les résolvait vers les enregistrements réels côté Python
(l'équivalent JS, kpiResoudreSourcesReelles, n'avait pas été porté à
l'Étape 2 — son périmètre se limitait au calcul). Signalé ici plutôt que
supposé implicitement inclus dans un travail déjà livré.
"""

from sqlalchemy import select

from .extracteur import TABLE_PAR_COLLECTION


def resoudre_sources(conn, metadata, kpi_value: dict) -> list[dict]:
    kpi_definitions = metadata.tables["kpi_definitions"]
    definition = conn.execute(
        select(kpi_definitions).where(
            kpi_definitions.c.id == kpi_value["kpi_id"],
            kpi_definitions.c.version == kpi_value["version"],
        )
    ).mappings().first()
    if definition is None:
        return []

    table_name = TABLE_PAR_COLLECTION.get(definition["source_collection"])
    if table_name is None:
        return []

    table = metadata.tables[table_name]
    ids = kpi_value["sources_ids"] or []
    if not ids:
        return []

    stmt = select(table).where(table.c.id.in_(ids))
    rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]
