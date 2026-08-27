"""
auth.py — Vérification des tokens JWT émis par Supabase Auth (Étape 4).

MISE À JOUR (ADR-037) : Supabase impose désormais la signature asymétrique
(ES256, clés "JWT Signing Keys") pour les nouveaux projets, sans option de
retour à l'ancien secret partagé HS256 — confirmé directement par
Abdeljalil depuis son Dashboard. La vérification passe donc par le point
de publication des clés publiques (JWKS), pas par un secret à connaître.

Différence de principe avec l'ancienne approche : en HS256, le serveur qui
vérifie doit connaître le même secret que celui qui signe (un secret qui
fuit permet de forger des tokens). En ES256/JWKS, seule la clé PUBLIQUE
est distribuée ; la clé privée ne quitte jamais les serveurs de Supabase.
Aucun secret à protéger côté APEX pour la vérification elle-même.
"""

import os
from fastapi import Header, HTTPException, Depends
from jwt import PyJWKClient, decode as jwt_decode
from jwt.exceptions import PyJWTError
from sqlalchemy import select

SUPABASE_URL = os.environ.get("SUPABASE_URL")  # ex: https://xxxx.supabase.co
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json" if SUPABASE_URL else None
ALGORITHMS = ["ES256"]  # les projets migrés n'émettent plus que ES256 ; pas de HS256 en repli (cf. ADR-037)
AUDIENCE = "authenticated"

# Client JWKS créé une seule fois (comme l'engine SQLAlchemy, ADR-032) :
# PyJWKClient met les clés en cache en mémoire et ne refait un appel réseau
# que si un "kid" inconnu apparaît (rotation de clé côté Supabase) — pas à
# chaque requête.
_jwks_client = None


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        if not JWKS_URL:
            raise HTTPException(
                status_code=500,
                detail="SUPABASE_URL non configuré côté serveur (voir .env.example).",
            )
        _jwks_client = PyJWKClient(JWKS_URL, cache_keys=True, lifespan=600)  # 10 min, aligné sur le cache Supabase Edge
    return _jwks_client


def verifier_token(authorization: str = Header(None)) -> dict:
    """Extrait et vérifie le token Bearer via JWKS/ES256. Lève 401 si
    absent ou invalide — jamais un 500 opaque."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant (en-tête Authorization: Bearer <token>).")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt_decode(token, signing_key.key, algorithms=ALGORITHMS, audience=AUDIENCE)
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalide : {e}")

    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="Token valide mais sans identifiant utilisateur (sub).")
    return payload


def utilisateur_courant(payload: dict = Depends(verifier_token)) -> dict:
    """Dépendance FastAPI réutilisable : renvoie {user_id, email} de
    l'utilisateur authentifié."""
    return {"user_id": payload["sub"], "email": payload.get("email")}


def verifier_acces_organisation(conn, metadata, user_id: str, concession_id: str) -> bool:
    """Vérifie que l'utilisateur est membre de l'organisation propriétaire
    de la concession demandée (ADR-035, ADR-026). Renvoie True/False —
    l'appelant décide du code HTTP (403) à lever."""
    concessions = metadata.tables["concessions"]
    membres = metadata.tables["membres_organisation"]

    organisation_id = conn.execute(
        select(concessions.c.organisation_id).where(concessions.c.id == concession_id)
    ).scalar()
    if organisation_id is None:
        return False  # concession inexistante — traité comme non autorisé, pas une 500

    membre = conn.execute(
        select(membres).where(
            membres.c.user_id == user_id,
            membres.c.organisation_id == organisation_id,
        )
    ).first()
    return membre is not None
