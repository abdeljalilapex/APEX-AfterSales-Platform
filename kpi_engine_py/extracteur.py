"""
extracteur.py — Port fidèle de kpiExtraireDonnees() (JavaScript) vers Python.

Remplace l'ancienne fonction JS `filtre` par l'interprétation du champ
déclaratif `source_critere` (JSONB), conformément à ADR-021.

------------------------------------------------------------------
MISE À JOUR (ADR-031) : la colonne de date utilisée pour le filtrage par
période était auparavant codée en dur ici (COLONNE_DATE_PAR_COLLECTION),
écart signalé explicitement à ADR-027. Le schéma porte désormais
`kpi_definitions.date_champ_periode` (colonne réelle) — cette information
est lue depuis la définition chargée en base, plus aucune correspondance
codée en dur dans ce module.
------------------------------------------------------------------
"""

from sqlalchemy import select, and_
import operator as _op

# Correspondance collection -> nom de table réelle. Reste nécessaire (le nom
# de la table n'est pas non plus déclaré dans kpi_definitions à ce stade) ;
# seule la colonne de DATE a été fermée par ADR-031, pas le nom de table.
TABLE_PAR_COLLECTION = {
    "rendezvous": "rendezvous",
    "ordresReparation": "ordres_reparation",
}

# Taxonomie des opérateurs supportés par source_critere — volontairement
# restreinte aux comparaisons simples (cohérent avec le rejet déjà acté
# d'un langage de règles complet, ADR-007). "=" est le seul opérateur
# utilisé par les KPIDefinition existantes ; les autres sont ajoutés par
# anticipation minimale (coût quasi nul, même taxonomie que kpiCalculerAgregation),
# pas par sur-ingénierie.
OPERATEURS = {
    "=": _op.eq,
    "!=": _op.ne,
    ">": _op.gt,
    "<": _op.lt,
    ">=": _op.ge,
    "<=": _op.le,
}


def extraire_donnees(conn, metadata, kpi_definition: dict, periode_debut, periode_fin, concession_id):
    """
    Lit les enregistrements de la collection source d'une KPIDefinition,
    filtrés par concession, par période réelle (dates), et par le critère
    déclaratif source_critere s'il existe.

    Retourne une liste de dict (une ligne = un enregistrement source).
    """
    collection = kpi_definition["source_collection"]
    if collection not in TABLE_PAR_COLLECTION:
        raise ValueError(
            f"Extracteur — collection source inconnue : '{collection}'."
        )
    table_name = TABLE_PAR_COLLECTION[collection]
    colonne_date = kpi_definition["date_champ_periode"]  # lu depuis la base (ADR-031), plus codé en dur
    table = metadata.tables[table_name]

    conditions = [
        table.c.concession_id == concession_id,
        table.c[colonne_date] >= periode_debut,
        table.c[colonne_date] <= periode_fin,
    ]

    critere = kpi_definition.get("source_critere")
    if critere:
        champ = critere["champ"]
        op_symbole = critere["operateur"]
        valeur = critere["valeur"]
        if op_symbole not in OPERATEURS:
            raise ValueError(
                f"Extracteur — opérateur '{op_symbole}' non supporté. "
                f"Opérateurs disponibles : {list(OPERATEURS.keys())}."
            )
        conditions.append(OPERATEURS[op_symbole](table.c[champ], valeur))

    stmt = select(table).where(and_(*conditions))
    rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]
