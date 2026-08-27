"""
ecrivain.py — Port fidèle de kpiEcrireResultat() (JavaScript) vers PostgreSQL.

Différence assumée avec la version JS (pas un écart de logique, un
changement de mécanisme d'implémentation) : en JavaScript, le
dédoublonnage était fait à la main (recherche dans un tableau puis
Object.assign). En SQL, on s'appuie directement sur la contrainte UNIQUE
déjà présente dans le schéma (kpi_id, version, periode_debut, periode_fin,
concession_id) via INSERT ... ON CONFLICT ... DO UPDATE — comme demandé,
"ne pas la contourner, s'appuyer dessus".

Règle de recalcul (ADR-015), inchangée : recalcul automatique, silencieux,
horodatage de recalcul mis à jour ; cree_le et cree_par ne sont JAMAIS
réécrits lors d'un recalcul — un recalcul ne change pas la paternité ni la
date de création d'origine (même règle que dans le prototype JS).
"""

from sqlalchemy.dialects.postgresql import insert as pg_insert


def ecrire_resultat(conn, metadata, resultat: dict, sources_ids: list, auteur: str = "system"):
    kpi_values = metadata.tables["kpi_values"]

    stmt = pg_insert(kpi_values).values(
        kpi_id=resultat["kpi_id"],
        version=resultat["version"],
        periode_debut=resultat["periode_debut"],
        periode_fin=resultat["periode_fin"],
        concession_id=resultat["concession_id"],
        valeur=resultat["valeur"],
        statut=resultat["statut"],
        sources_ids=sources_ids,
        nb_enregistrements_sources=len(sources_ids),
        cree_par=auteur,
        # cree_le et recalcule_le : valeurs par défaut du schéma (now()) à
        # la création ; recalcule_le explicitement mis à jour ci-dessous
        # uniquement dans la branche de conflit (recalcul), jamais à la
        # création initiale — cohérent avec le prototype JS où
        # recalculeLe vaut null à la première écriture.
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=["kpi_id", "version", "periode_debut", "periode_fin", "concession_id"],
        set_={
            "valeur": stmt.excluded.valeur,
            "statut": stmt.excluded.statut,
            "sources_ids": stmt.excluded.sources_ids,
            "nb_enregistrements_sources": stmt.excluded.nb_enregistrements_sources,
            "recalcule_le": _now_expr(),
            # cree_le et cree_par volontairement absents du SET : ils
            # conservent la valeur déjà écrite lors de la création d'origine.
        },
    ).returning(kpi_values)

    row = conn.execute(stmt).mappings().first()
    conn.commit()
    return dict(row)


def _now_expr():
    from sqlalchemy import func
    return func.now()
