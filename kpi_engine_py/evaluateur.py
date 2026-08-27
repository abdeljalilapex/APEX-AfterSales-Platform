"""
evaluateur.py — Port fidèle de kpiEvaluerStatut() (JavaScript).

Même convention par pourcentage d'atteinte de l'objectif, mêmes seuils
(>=100 excellent, >=90 watch, >=75 moderate, sinon critical), même
traitement d'une valeur insuffisante (None -> 'watch', jamais 'excellent'
par défaut).
"""


def evaluer_statut(valeur, definition: dict):
    if valeur is None:
        return "watch"
    target = definition.get("target")
    if not target:
        return None  # KPI sans objectif défini : pas de statut évalué
    target = float(target)  # PostgreSQL NUMERIC -> Decimal ; Python float attendu pour l'arithmétique
    lower_better = definition.get("lower_better", False)
    pct = (target / valeur) * 100 if lower_better else (valeur / target) * 100
    if pct >= 100:
        return "excellent"
    if pct >= 90:
        return "watch"
    if pct >= 75:
        return "moderate"
    return "critical"
