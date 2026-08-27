"""
db.py — Connexion à PostgreSQL et réflexion du schéma existant.

Choix de bibliothèque (documenté en détail dans ADR-027) : SQLAlchemy Core,
sans mapping ORM déclaratif, avec réflexion automatique des tables
(MetaData.reflect) plutôt que des modèles Python réécrits à la main.

Pourquoi ce choix précis :
- psycopg2 brut aurait exigé du SQL écrit à la main pour chaque nouvelle
  collection source, sans réutilisation possible entre KPI.
- Un ORM déclaratif (classes Python mappées table par table) aurait dupliqué
  la définition du schéma déjà présente dans APEX_schema.sql — deux sources
  de vérité pour la même structure, exactement le type d'incohérence que ce
  projet a déjà corrigé à plusieurs reprises (cf. ADR-012, principe des 3
  niveaux Business Model / Architecture / Implémentation).
- La réflexion automatique lit la structure réelle de la base à l'exécution :
  APEX_schema.sql reste l'unique source de vérité, aucun modèle à maintenir
  en parallèle.
- SQLAlchemy Core (pas l'ORM complet) est également le choix le plus naturel
  pour une réutilisation future par FastAPI (Etape API), qui s'appuie
  couramment sur le même moteur de connexion.
"""

from sqlalchemy import create_engine, MetaData
import os

# Lu depuis la variable d'environnement DATABASE_URL si définie (ex: pour
# pointer vers Supabase), sinon repli sur PostgreSQL local (développement).
# Le mot de passe réel ne doit JAMAIS être codé en dur dans ce fichier —
# uniquement transmis via l'environnement, jamais commité.
DEFAULT_DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:test@localhost:5432/apex_test",
)


def get_engine(dsn: str = None):
    """Crée un engine SQLAlchemy. dsn injectable explicitement, sinon lu
    depuis DATABASE_URL, sinon repli local."""
    return create_engine(dsn or DEFAULT_DSN, future=True)


def reflect_metadata(engine):
    """Lit la structure réelle des tables depuis PostgreSQL — pas de
    modèle Python à maintenir en double du schéma SQL."""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata
