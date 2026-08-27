"""
main.py — API FastAPI, Étape 3 (routes) + Étape 4 (authentification Supabase).

Expose le moteur KPI déjà porté (kpi_engine_py, Étape 2) sans aucune
réécriture de sa logique : cette couche route, authentifie, autorise, et
sérialise — le calcul reste entièrement dans kpi_engine_py.

Gestion de connexion (ADR-032) : engine + métadonnées créés une seule fois
au démarrage (lifespan) ; connexion par requête via Depends.

Authentification (Étape 4) : chaque route exige un token Bearer valide
(Supabase Auth, JWT vérifié dans auth.py). Les routes portant sur une
concession_id vérifient en plus que l'utilisateur appartient à
l'organisation propriétaire de cette concession (ADR-035) — sinon 403.
Le champ "auteur" transmis par le client dans CalculerRequest est
désormais IGNORÉ pour l'écriture (cree_par) : c'est l'identité extraite
du token qui fait foi, jamais une valeur fournie librement par l'appelant
(un client ne doit jamais pouvoir usurper l'identité d'un autre auteur).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException

from kpi_engine_py import get_engine, reflect_metadata
from kpi_engine_py.engine import calculate as engine_calculate
from kpi_engine_py.provenance import resoudre_sources
from sqlalchemy import select

from .schemas import KPIDefinitionOut, CalculerRequest, KPIValueOut, SourceRecordOut
from .auth import utilisateur_courant, verifier_acces_organisation

_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    metadata = reflect_metadata(engine)
    _state["engine"] = engine
    _state["metadata"] = metadata
    yield
    _state.clear()


app = FastAPI(title="APEX KPI Engine API", version="0.2.0", lifespan=lifespan)


def get_conn():
    conn = _state["engine"].connect()
    try:
        yield conn
    finally:
        conn.close()


def get_metadata():
    return _state["metadata"]


def _exiger_acces_organisation(conn, metadata, user_id: str, concession_id: str):
    if not verifier_acces_organisation(conn, metadata, user_id, concession_id):
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : vous n'êtes pas membre de l'organisation propriétaire de cette concession.",
        )


@app.get("/health")
def health():
    # Volontairement public — pas de JWT exigé, sinon un load balancer ne
    # pourrait jamais vérifier que le service tourne.
    return {"statut": "ok"}


@app.get("/kpi-definitions", response_model=list[KPIDefinitionOut])
def lister_definitions(conn=Depends(get_conn), metadata=Depends(get_metadata),
                        utilisateur: dict = Depends(utilisateur_courant)):
    # Authentification requise, pas d'autorisation par organisation : les
    # définitions de KPI ne sont pas propres à une concession.
    table = metadata.tables["kpi_definitions"]
    rows = conn.execute(select(table)).mappings().all()
    return [dict(r) for r in rows]


@app.post("/kpi/{kpi_id}/calculer", response_model=KPIValueOut)
def calculer(kpi_id: str, requete: CalculerRequest, conn=Depends(get_conn), metadata=Depends(get_metadata),
             utilisateur: dict = Depends(utilisateur_courant)):
    _exiger_acces_organisation(conn, metadata, utilisateur["user_id"], requete.concession_id)
    try:
        resultat = engine_calculate(
            conn, metadata, kpi_id,
            requete.periode_debut, requete.periode_fin, requete.concession_id,
            version=requete.version,
            auteur=utilisateur["user_id"],  # identité réelle du token, jamais celle fournie par le client
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return resultat


@app.get("/kpi/{kpi_id}/valeurs", response_model=list[KPIValueOut])
def lister_valeurs(kpi_id: str, concession_id: str, conn=Depends(get_conn), metadata=Depends(get_metadata),
                    utilisateur: dict = Depends(utilisateur_courant)):
    # concession_id devient obligatoire (plus optionnelle) : impossible de
    # lister sans savoir sur quelle organisation vérifier l'autorisation.
    _exiger_acces_organisation(conn, metadata, utilisateur["user_id"], concession_id)
    table = metadata.tables["kpi_values"]
    stmt = select(table).where(table.c.kpi_id == kpi_id, table.c.concession_id == concession_id)
    stmt = stmt.order_by(table.c.periode_debut)
    rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]


@app.get("/kpi-values/{value_id}/sources", response_model=list[SourceRecordOut])
def sources_kpi_value(value_id: str, conn=Depends(get_conn), metadata=Depends(get_metadata),
                       utilisateur: dict = Depends(utilisateur_courant)):
    table = metadata.tables["kpi_values"]
    kv = conn.execute(select(table).where(table.c.id == value_id)).mappings().first()
    if kv is None:
        raise HTTPException(status_code=404, detail=f"KPIValue introuvable : {value_id}")
    _exiger_acces_organisation(conn, metadata, utilisateur["user_id"], str(kv["concession_id"]))
    enregistrements = resoudre_sources(conn, metadata, dict(kv))
    return [{"id": str(r["id"]), "donnees": {k: str(v) for k, v in r.items()}} for r in enregistrements]

