"""
calculateur.py — Port fidèle de kpiCalculerAgregation() (JavaScript).

Aucune divergence de logique par rapport à la version JS : mêmes 4 types
d'agrégation, même règle explicite pour l'échantillon vide (None, jamais
une exception ni une valeur type NaN qui n'existe pas nativement en
JSON/SQL de la même façon qu'en JS).
"""


def calculer_agregation(agregation: dict, data: list[dict]):
    type_agregation = agregation["type"]
    champ = agregation.get("champ")

    if type_agregation == "comptage":
        return len(data)

    if type_agregation == "somme":
        return sum(float(r.get(champ) or 0) for r in data)

    if type_agregation == "moyenne":
        if len(data) == 0:
            return None  # donnée insuffisante — jamais de division par zéro silencieuse
        return sum(float(r.get(champ) or 0) for r in data) / len(data)

    if type_agregation == "ratio":
        champ_numerateur_filtre = agregation.get("champ_numerateur_filtre")
        if not champ_numerateur_filtre or len(data) == 0:
            return None
        num = sum(1 for r in data if champ_numerateur_filtre(r))
        return num / len(data)

    raise ValueError(f"Calculateur — type d'agrégation inconnu : {type_agregation}")
