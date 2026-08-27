-- ============================================================
-- APEX — SCHÉMA POSTGRESQL
-- Traduction du Data Model conceptuel (APEX_Data_Model.md, 26 entités)
-- Étape 1 du pivot backend — schéma uniquement, aucune API, aucune
-- authentification à ce stade.
--
-- Écarts par rapport au modèle conceptuel : documentés en fin de
-- fichier et dans APEX_Backend_Migration_Notes.md / ADR-021.
-- ============================================================

-- ---- Extension pour identifiants UUID ----
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 0. ORGANISATION (ADR-026 — frontière d'isolation entre clients
-- payants d'APEX, referme la question ouverte d'ADR-024)
-- ============================================================
CREATE TABLE organisations (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom                     TEXT NOT NULL,
    date_debut_abonnement   DATE NOT NULL DEFAULT CURRENT_DATE,
    statut                  TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif','suspendu','resilie')),
    cree_le                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 1. CONCESSION (transverse — cf. ADR-005)
-- ------------------------------------------------------------
-- ADR-026 : concessions appartient désormais à une organisation
-- (une organisation peut posséder plusieurs concessions). La
-- frontière d'isolation entre clients payants d'APEX est
-- organisation_id, pas concession_id — concession_id reste la
-- granularité interne (comparer des établissements d'un même client).
-- ============================================================
CREATE TABLE concessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id     UUID NOT NULL REFERENCES organisations(id),
    nom             TEXT NOT NULL,
    adresse         TEXT,
    marques         TEXT[] NOT NULL DEFAULT '{}',
    capacite_atelier INTEGER,
    cree_le         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 2. UTILISATEUR / ROLE (préparé, non exploité avant l'authentification réelle)
-- ============================================================
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom             TEXT NOT NULL UNIQUE,
    permissions     JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE utilisateurs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifiant         TEXT NOT NULL UNIQUE,
    nom                 TEXT NOT NULL,
    statut              TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif','inactif')),
    derniere_connexion  TIMESTAMPTZ,
    cree_le             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE utilisateur_roles (
    utilisateur_id  UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (utilisateur_id, role_id)
);

-- Accès multi-concession d'un utilisateur (ex: Direction Générale)
CREATE TABLE utilisateur_concessions (
    utilisateur_id  UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    concession_id   UUID NOT NULL REFERENCES concessions(id) ON DELETE CASCADE,
    PRIMARY KEY (utilisateur_id, concession_id)
);

-- ============================================================
-- MEMBRES_ORGANISATION (ADR-035) — rattache un utilisateur Supabase Auth
-- (auth.users, schéma propre à Supabase) à une ou plusieurs organisations.
-- Pas de FK réelle sur user_id (limite cross-schéma déjà documentée pour
-- historique_statut.entite_id, ADR-021) : l'intégrité est assurée côté
-- application (l'API ne fait confiance qu'à un user_id extrait d'un JWT
-- valide, jamais saisi librement).
-- ============================================================
CREATE TABLE membres_organisation (
    user_id         UUID NOT NULL,
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL DEFAULT 'membre',
    PRIMARY KEY (user_id, organisation_id)
);

-- ============================================================
-- 3. RESSOURCES ATELIER : POSTE / TECHNICIEN / CONSEILLER SERVICE
-- ============================================================
CREATE TABLE postes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type            TEXT NOT NULL,
    concession_id   UUID NOT NULL REFERENCES concessions(id)
);

CREATE TABLE techniciens (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id      UUID UNIQUE REFERENCES utilisateurs(id),
    nom                 TEXT NOT NULL,
    poste_habituel_id   UUID REFERENCES postes(id),
    concession_id       UUID NOT NULL REFERENCES concessions(id),
    statut              TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif','absent'))
);

-- Spécialités : relation N-N normalisée (le Data Model conceptuel
-- portait un tableau de spécialités directement sur Technicien).
CREATE TABLE technicien_specialites (
    technicien_id   UUID NOT NULL REFERENCES techniciens(id) ON DELETE CASCADE,
    specialite      TEXT NOT NULL,
    PRIMARY KEY (technicien_id, specialite)
);

CREATE TABLE conseillers_service (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id  UUID UNIQUE REFERENCES utilisateurs(id),
    nom             TEXT NOT NULL,
    concession_id   UUID NOT NULL REFERENCES concessions(id)
);

-- ============================================================
-- 4. FOURNISSEUR / PIECE
-- ============================================================
CREATE TABLE fournisseurs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom                 TEXT NOT NULL,
    delai_moyen_jours   NUMERIC(5,2),
    fiabilite_pct       NUMERIC(5,2)
);

CREATE TABLE pieces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    designation     TEXT NOT NULL,
    prix_catalogue  NUMERIC(10,2) NOT NULL CHECK (prix_catalogue >= 0),
    fournisseur_id  UUID REFERENCES fournisseurs(id),
    stock           INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    seuil_reappro   INTEGER NOT NULL DEFAULT 0,
    concession_id   UUID NOT NULL REFERENCES concessions(id)
);

-- ============================================================
-- 5. CLIENT / VEHICULE
-- ============================================================
CREATE TABLE clients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom                 TEXT NOT NULL,
    concession_id       UUID NOT NULL REFERENCES concessions(id),
    date_first_visite   DATE,
    statut              TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif','inactif')),
    preference_contact  TEXT CHECK (preference_contact IN ('SMS','Email','Téléphone'))
);

CREATE TABLE vehicules (
    id                              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id                       UUID NOT NULL REFERENCES clients(id),
    concession_id                   UUID NOT NULL REFERENCES concessions(id),
    marque                          TEXT NOT NULL,
    modele                          TEXT NOT NULL,
    motorisation                    TEXT NOT NULL CHECK (motorisation IN ('thermique','hybride','électrique')),
    kilometrage                     INTEGER CHECK (kilometrage >= 0),
    date_mise_circulation           DATE,
    statut_garantie_constructeur    BOOLEAN NOT NULL DEFAULT false
);

-- ============================================================
-- 6. RENDEZ-VOUS
-- ============================================================
CREATE TABLE rendezvous (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id               UUID NOT NULL REFERENCES clients(id),
    vehicule_id             UUID NOT NULL REFERENCES vehicules(id),
    concession_id           UUID NOT NULL REFERENCES concessions(id),
    date_demande            TIMESTAMPTZ NOT NULL,
    date_creneau_confirme   TIMESTAMPTZ,
    delai_obtention_jours   NUMERIC(5,2),
    canal                   TEXT NOT NULL CHECK (canal IN ('Téléphone','Digital')),
    statut                  TEXT NOT NULL CHECK (statut IN ('honore','no_show','annule'))
);

-- ============================================================
-- 7. DEVIS / ORDRE DE RÉPARATION
-- ------------------------------------------------------------
-- Écart documenté (ADR-021) : le modèle conceptuel décrivait une
-- relation bidirectionnelle Devis <-> OrdreReparation. En relationnel,
-- une seule direction est conservée (OrdreReparation référence Devis) ;
-- l'autre sens se retrouve par une requête, pas par une colonne
-- redondante — évite un cycle de clés étrangères.
-- ============================================================
CREATE TABLE devis (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concession_id           UUID NOT NULL REFERENCES concessions(id),
    conseiller_service_id   UUID NOT NULL REFERENCES conseillers_service(id),
    montant                 NUMERIC(10,2) NOT NULL CHECK (montant >= 0),
    statut                  TEXT NOT NULL CHECK (statut IN ('valide','partiel','refuse','en_attente')),
    delai_validation_jours  NUMERIC(5,2),
    cree_le                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ordres_reparation (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rendezvous_id           UUID REFERENCES rendezvous(id),
    devis_id                UUID NOT NULL REFERENCES devis(id),
    client_id               UUID NOT NULL REFERENCES clients(id),
    vehicule_id             UUID NOT NULL REFERENCES vehicules(id),
    technicien_id           UUID NOT NULL REFERENCES techniciens(id),
    conseiller_service_id   UUID NOT NULL REFERENCES conseillers_service(id),
    poste_id                UUID NOT NULL REFERENCES postes(id),
    concession_id           UUID NOT NULL REFERENCES concessions(id),
    date_ouverture          TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_cloture            TIMESTAMPTZ,
    statut                  TEXT NOT NULL CHECK (statut IN ('ouvert','en_cours','controle_non_conforme','clos'))
);

CREATE TABLE interventions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devis_id                UUID NOT NULL REFERENCES devis(id),
    ordre_reparation_id     UUID REFERENCES ordres_reparation(id),
    libelle                 TEXT NOT NULL,
    temps_bareme_min        INTEGER NOT NULL CHECK (temps_bareme_min > 0)
);

CREATE TABLE lignes_pieces (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id     UUID NOT NULL REFERENCES ordres_reparation(id),
    piece_id                UUID NOT NULL REFERENCES pieces(id),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    statut                  TEXT NOT NULL CHECK (statut IN ('en_stock','commandee')),
    prix_applique           NUMERIC(10,2) NOT NULL
);

CREATE TABLE temps_main_oeuvre (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intervention_id         UUID NOT NULL REFERENCES interventions(id),
    technicien_id           UUID NOT NULL REFERENCES techniciens(id),
    duree_reelle_min        INTEGER NOT NULL CHECK (duree_reelle_min > 0)
);

CREATE TABLE controles_qualite (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id         UUID NOT NULL UNIQUE REFERENCES ordres_reparation(id),
    statut                      TEXT NOT NULL CHECK (statut IN ('conforme','non_conforme')),
    controleur_utilisateur_id   UUID REFERENCES utilisateurs(id),
    date_controle               TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE garanties (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id     UUID NOT NULL REFERENCES ordres_reparation(id),
    vehicule_id             UUID NOT NULL REFERENCES vehicules(id),
    type                    TEXT NOT NULL CHECK (type IN ('garantie_standard','extension','rappel_constructeur')),
    statut                  TEXT NOT NULL CHECK (statut IN ('accepte','refuse','en_cours')),
    montant_pris_en_charge  NUMERIC(10,2)
);

CREATE TABLE factures (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id     UUID NOT NULL UNIQUE REFERENCES ordres_reparation(id),
    client_id               UUID NOT NULL REFERENCES clients(id),
    montant_ttc             NUMERIC(10,2) NOT NULL CHECK (montant_ttc >= 0),
    statut_paiement         TEXT NOT NULL CHECK (statut_paiement IN ('paye','en_attente')),
    emise_le                TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 8. SATISFACTION CLIENT
-- ============================================================
CREATE TABLE enquetes_satisfaction (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id UUID NOT NULL REFERENCES ordres_reparation(id),
    client_id           UUID NOT NULL REFERENCES clients(id),
    date_envoi          TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_reponse        TIMESTAMPTZ,
    score               NUMERIC(3,1) CHECK (score BETWEEN 0 AND 10),
    verbatim            TEXT
);

CREATE TABLE reclamations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordre_reparation_id UUID REFERENCES ordres_reparation(id),
    client_id           UUID NOT NULL REFERENCES clients(id),
    categorie            TEXT NOT NULL,
    description          TEXT,
    statut               TEXT NOT NULL DEFAULT 'ouverte' CHECK (statut IN ('ouverte','en_cours','resolue')),
    action_corrective    TEXT
);

-- ============================================================
-- 9. NOTIFICATIONS / PROJETS D'AMÉLIORATION
-- ============================================================
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id  UUID REFERENCES utilisateurs(id),
    niveau          TEXT NOT NULL CHECK (niveau IN ('excellent','watch','moderate','critical')),
    titre           TEXT NOT NULL,
    description     TEXT,
    module_source   TEXT,
    date            TIMESTAMPTZ NOT NULL DEFAULT now(),
    lu              BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE projets_amelioration (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom             TEXT NOT NULL,
    type            TEXT NOT NULL CHECK (type IN ('Lean','Kaizen','5S','Six Sigma','Digitalisation','Formation','Innovation')),
    objectif        TEXT,
    responsable     TEXT,
    budget          NUMERIC(10,2),
    avancement      INTEGER NOT NULL DEFAULT 0 CHECK (avancement BETWEEN 0 AND 100),
    statut          TEXT NOT NULL DEFAULT 'Cadrage'
);

-- ============================================================
-- 10. KPI ENGINE : KPIDEFINITION / KPIVALUE
-- ------------------------------------------------------------
-- Écart documenté (ADR-021) : dans le code HTML, KPIDefinition.source.filtre
-- est une fonction JavaScript (ex: r => r.statut === 'honore'). Une fonction
-- ne se stocke pas en base — remplacée ici par un critère déclaratif JSONB
-- ({"champ":"statut","operateur":"=","valeur":"honore"}) que le futur
-- backend devra interpréter. C'est un changement de représentation, pas
-- de logique : la même règle métier reste exprimée, sous une forme que
-- PostgreSQL peut stocker.
-- ============================================================
CREATE TABLE kpi_definitions (
    id                      TEXT NOT NULL,
    version                 INTEGER NOT NULL DEFAULT 1,
    nom                     TEXT NOT NULL,
    description             TEXT,
    unite                   TEXT,
    frequence_calcul        TEXT NOT NULL DEFAULT 'hebdomadaire',
    target                  NUMERIC,
    lower_better            BOOLEAN NOT NULL DEFAULT false,
    source_collection       TEXT NOT NULL,
    source_critere          JSONB,             -- remplace la fonction "filtre" du prototype HTML
    -- ADR-031 : ferme l'écart signalé à ADR-027 — précise quelle colonne de
    -- date de la collection source sert au filtrage par période, information
    -- auparavant codée en dur dans extracteur.py (COLONNE_DATE_PAR_COLLECTION).
    date_champ_periode      TEXT NOT NULL,
    agregation_type         TEXT NOT NULL CHECK (agregation_type IN ('comptage','somme','moyenne','ratio')),
    agregation_champ        TEXT,
    evenements_declencheurs TEXT[] DEFAULT '{}',
    PRIMARY KEY (id, version)
);

CREATE TABLE projet_kpi_definitions (
    projet_id           UUID NOT NULL REFERENCES projets_amelioration(id) ON DELETE CASCADE,
    kpi_definition_id   TEXT NOT NULL,
    kpi_definition_version INTEGER NOT NULL,
    PRIMARY KEY (projet_id, kpi_definition_id, kpi_definition_version),
    FOREIGN KEY (kpi_definition_id, kpi_definition_version) REFERENCES kpi_definitions(id, version)
);

CREATE TABLE kpi_values (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id                      TEXT NOT NULL,
    version                     INTEGER NOT NULL,
    -- Écart documenté (ADR-021) : "semaine" (étiquette texte S1/S2/S3 dans
    -- le prototype) devient une vraie période datée en base — condition
    -- pour des requêtes de comparaison réelles (>, <, BETWEEN) plutôt
    -- qu'un tri lexicographique sur une chaîne.
    periode_debut               DATE NOT NULL,
    periode_fin                 DATE NOT NULL,
    concession_id               UUID NOT NULL REFERENCES concessions(id),
    valeur                      NUMERIC,             -- NULL explicite = donnée insuffisante (jamais NaN)
    statut                      TEXT CHECK (statut IN ('excellent','watch','moderate','critical')),
    sources_ids                 UUID[] NOT NULL DEFAULT '{}',
    nb_enregistrements_sources  INTEGER NOT NULL DEFAULT 0,
    cree_le                     TIMESTAMPTZ NOT NULL DEFAULT now(),
    recalcule_le                TIMESTAMPTZ,
    cree_par                    TEXT NOT NULL DEFAULT 'system',
    FOREIGN KEY (kpi_id, version) REFERENCES kpi_definitions(id, version),
    UNIQUE (kpi_id, version, periode_debut, periode_fin, concession_id)
);

-- ============================================================
-- 11. HISTORIQUE DE STATUT
-- ------------------------------------------------------------
-- Écart documenté (ADR-021) : référence polymorphe (entite_type +
-- entite_id) — PostgreSQL ne peut pas exprimer une clé étrangère qui
-- pointe vers l'une de plusieurs tables selon la valeur d'une colonne.
-- Accepté sans contrainte FK sur entite_id, avec un CHECK limitant
-- entite_type aux tables concernées. Intégrité applicative à assurer
-- par le futur backend (pas par la base) — signalé explicitement plutôt
-- que résolu silencieusement, comme demandé.
-- ============================================================
CREATE TABLE historique_statut (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entite_type             TEXT NOT NULL CHECK (entite_type IN ('devis','ordre_reparation','controle_qualite')),
    entite_id               UUID NOT NULL,      -- pas de FK réelle : voir note ci-dessus
    statut_precedent        TEXT,
    nouveau_statut          TEXT NOT NULL,
    date_changement         TIMESTAMPTZ NOT NULL DEFAULT now(),
    auteur_utilisateur_id   UUID REFERENCES utilisateurs(id)
);

-- ============================================================
-- INDEX complémentaires (performance des filtres déjà utilisés par le
-- KPI Engine : par concession, par période, par statut)
-- ============================================================
CREATE INDEX idx_concessions_organisation ON concessions (organisation_id);
CREATE INDEX idx_ordres_reparation_concession_date ON ordres_reparation (concession_id, date_ouverture);
CREATE INDEX idx_rendezvous_concession_statut ON rendezvous (concession_id, statut);
CREATE INDEX idx_kpi_values_kpi_periode ON kpi_values (kpi_id, periode_debut, periode_fin);
CREATE INDEX idx_historique_statut_entite ON historique_statut (entite_type, entite_id);

-- ============================================================
-- NOTE (ADR-026) — dénormalisation envisagée puis écartée
-- ------------------------------------------------------------
-- Ajouter organisation_id directement sur chaque table filtrée par
-- concession (kpi_values, ordres_reparation, etc.) aurait évité une
-- jointure via concessions à chaque requête isolée par client. Écarté
-- à ce stade : aucune donnée de charge réelle ne justifie ce coût de
-- duplication (une organisation_id à maintenir en cohérence à deux
-- endroits à chaque écriture) ; l'index sur concessions.organisation_id
-- ci-dessus rend la jointure peu coûteuse pour les volumes actuels.
-- À reconsidérer si une mesure réelle de performance le justifie un
-- jour — pas par anticipation.
-- ============================================================
