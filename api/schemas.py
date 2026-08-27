"""
schemas.py — Modèles Pydantic de requête/réponse de l'API.

Aucune logique métier ici : ces modèles ne font que valider la forme des
échanges HTTP. Le calcul reste entièrement dans kpi_engine_py, inchangé.
"""

from datetime import date, datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel


class KPIDefinitionOut(BaseModel):
    id: str
    version: int
    nom: str
    description: Optional[str] = None
    unite: Optional[str] = None
    frequence_calcul: str
    target: Optional[float] = None
    lower_better: bool
    source_collection: str
    date_champ_periode: str
    agregation_type: str
    agregation_champ: Optional[str] = None


class CalculerRequest(BaseModel):
    periode_debut: date
    periode_fin: date
    concession_id: str
    version: Optional[int] = None
    # Pas de champ "auteur" : l'identité provient exclusivement du token
    # JWT vérifié (Étape 4), jamais d'une valeur fournie par le client.


class KPIValueOut(BaseModel):
    id: UUID
    kpi_id: str
    version: int
    periode_debut: date
    periode_fin: date
    concession_id: UUID
    valeur: Optional[float] = None
    statut: Optional[str] = None
    nb_enregistrements_sources: int
    cree_le: datetime
    recalcule_le: Optional[datetime] = None
    cree_par: str


class SourceRecordOut(BaseModel):
    id: UUID
    donnees: dict[str, Any]
