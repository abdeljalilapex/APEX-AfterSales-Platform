# APEX_CHANGELOG.md 

## Historique du projet — Plateforme de pilotage Après-Vente AutoPerf Group (simulation) 

Note sur les dates : ce projet avance par sessions de travail successives plutôt que sur un calendrier fixe. Les dates ci-dessous correspondent aux sessions réelles de développement, à titre indicatif. 

## — [v1.0] AVOS (After-Sales Operating System) 

Date : Session 1 

### Modifications 

Première application de pilotage Après-Vente en fichier HTML autonome. 

- 15 modules : Executive Summary, Dashboard KPI, Performance Atelier, RH, Pièces de Rechange, Garantie, Sinistre, Satisfaction Client, Finance, Veille Concurrentielle, Tendances du Marché, Innovation, KPI personnalisés, Décisions du Directeur, Plan d'Actions, Gestion des Risques. 

- Sidebar collapsible, top bar, splash screen d'ouverture, jauges radiales sur les cartes KPI, graphiques Chart.js (bar, line, radar, doughnut, pie). 

- Données 100 % simulées, structurées dans un objet `REPORTS` unique pour faciliter l'ajout de rapports futurs. 

### Bugs corrigés 

- Défilement bloqué dans la sidebar et la zone de contenu (les éléments internes ne défilaient pas, coupant l'accès à certaines sections comme "Décisions du Directeur"). Cause : absence de `min-height:0` sur les conteneurs flex/grid imbriqués — bug CSS classique. Corrigé par ajout de `min-height:0` sur `#sidebar` , `#main` , `.sb-nav` , `#content` . 

### Refactoring 

Aucun (première version). 

### Décisions importantes 

Architecture "un seul fichier HTML autonome" retenue pour garantir l'ouverture sans installation. 

Toutes les données centralisées dans un objet JS unique ( `REPORTS` ) pour permettre l'ajout de futurs rapports sans toucher au code de rendu. 

## — [v2.0] APEX (After-Sales Performance Excellence Platform) 

Date : Session 2 

### Modifications 

- Renommage du projet AVOS → APEX, montée en gamme vers une architecture applicative modulaire (inspirée SAP Fiori, Dynamics 365, Salesforce, ServiceNow). Ajout d'un écran de connexion (identifiants démo) suivi d'un écran de bienvenue personnalisé. 

- Ajout de 6 nouveaux modules : Notifications (centre historisé et filtrable), Timeline (comparaison de semaines), Intelligence Center (fusion Veille + Marché + Innovation + SWOT générée automatiquement), AI Advisor (recommandations quotidiennes), Improvement Projects (portefeuille Lean/Kaizen/5S/Six Sigma avec budget et ROI), Knowledge Base. 

- Ajout de la recherche globale (topbar) indexant KPI, projets, techniciens, décisions, base de connaissance. 

Ajout des modules Administration et Mon Profil (V1 fonctionnelle simplifiée). 

- Ajout d'une seconde semaine de données simulées (Semaine 02) pour permettre les comparaisons de périodes. 

- Centre de Décision étendu à 5 priorités (au lieu de 3) + KPI à améliorer immédiatement + projets à démarrer. 

### Bugs corrigés 

Aucun bug hérité de la v1.0 identifié à ce stade (le bug de défilement avait déjà été corrigé en v1.0). 

### Refactoring 

Aucun refactoring structurel : priorité donnée aux fonctionnalités demandées. C'est ce constat qui a motivé l'audit ayant précédé la v3.0. 

### Décisions importantes 

Refus assumé de l'architecture multi-fichiers avec `data/*.json` proposée initialement : incompatible avec une ouverture locale en `file://` (blocage CORS). Architecture conservée en fichier unique. 

- Écran de connexion explicitement documenté comme prototype UX, non sécurisé (mot de passe visible côté client). 

AI Advisor implémenté comme contenu textuel structuré pré-rédigé, pas comme génération dynamique réelle — limitation assumée et à traiter en v3.0/v4.0. 

## — [Audit] Design Review APEX v2.0 

Date : Session 3 (analyse uniquement, aucun code produit) 

### Modifications 

Aucune (mission d'audit, pas de développement). 

### Constats principaux 

Fichier unique de 1 996 lignes / ~110 Ko : encore raisonnable en taille, mais architecture monolithique atteignant sa limite (données, logique et présentation mélangées). 

Duplication de code significative (cartes KPI, tableaux, badges reconstruits dans chaque vue). 

Fuite mémoire identifiée : instances Chart.js jamais détruites avant recréation. Risque XSS latent si des données saisies par un utilisateur réel entrent un jour dans le système (injection HTML sans échappement). 

21 items de menu jugés excessifs du point de vue UX. 

### Décisions importantes 

Décision produit : ne pas migrer vers un backend/base de données maintenant. Priorité donnée à un refactoring en architecture HTML autonome, préparant une migration future sans la réaliser prématurément. 

Adoption d'un plan de refactoring en 3 livrables (Fondations / Modularisation / Finalisation) plutôt qu'une réécriture en un seul bloc. 

## — [v3.0 Livrable 1 "Fondations"] 

Date : Session 4 

### Modifications 

- Introduction de la couche DATA clairement délimitée et documentée en tête de script. Introduction de la couche REPOSITORY ( `Repository` ) : point d'accès unique à toutes les données ( `REPORTS` , `PROJECTS` , `NOTIFICATIONS` , `KNOWLEDGE_BASE` , `AI_ADVISOR` , `SWOT` ). Toutes les vues, la recherche globale, la timeline et le centre de notifications 

- ont été reconnectés pour passer exclusivement par cette couche. 

Introduction de la couche STATE ( `AppState` ) : centralisation de la semaine active et de la sélection de comparaison Timeline, remplaçant deux variables globales dispersées ( `currentWeek` , `tlSelected` ). 

Aucun changement visuel ni fonctionnel voulu : ce livrable est une consolidation interne pure. 

### Bugs corrigés 

- Désynchronisation semaine par défaut : le sélecteur affichait "Semaine 02" par défaut alors que l'application chargeait réellement les données de la Semaine 01 au démarrage. Corrigé par alignement de l'état initial d' `AppState` avec l'option sélectionnée par défaut dans l'interface. 

### Refactoring 

- Réorganisation complète de l'ordre des sections du script pour respecter l'architecture en couches (DATA complète → REPOSITORY → STATE → Navigation → Composants/Vues → Contrôleur). Remplacement de tous les accès directs aux données globales par des appels `Repository.getXxx()` dans : recherche globale, timeline, notifications, décisions, 

- projets, base de connaissance, graphiques. Remplacement des variables globales `currentWeek` et `tlSelected` par `AppState.getCurrentWeek()/setCurrentWeek()` et `AppState.getTimelineSelection()/setTimelineSelection()/resetTimelineSelection()` . 

### Décisions importantes 

- Confirmation du choix de rester en fichier HTML autonome pour la v3.0 et probablement la v4.0 ; le passage à un backend reste une décision future, conditionnée à un vrai besoin (multi-utilisateur, persistance réelle), pas à la seule possibilité technique. 

- Méthode de travail formalisée pour la suite du projet : Rapport technique + Analyse des risques à chaque livrable ; Changelog mis à jour à chaque livrable ; Documentation d'architecture et Roadmap mises à jour à chaque version majeure (pas à chaque livrable intermédiaire). 

## — [v3.0 Livrable 2 "Modularisation"] 

Date : Session 5 

### Modifications 

Introduction de la couche COMPONENTS ( `Components` ), structurée en deux étages : un primitif unique ( `card()` ) et des composites construits par-dessus ( `statCard` , 

`tableCard` , `table` , `alertRow` , `alertList` , `gaugeBlock` , `gaugeSvg` , `kpiCard` , `statusPill` , `progressBar` , `trendArrow` ). 

- Réécriture de 13 vues (Home, RH, Pièces, Garantie, Sinistre, Satisfaction, Finance, Intelligence Center, Décisions, Administration, KPI Center, Improvement Projects, centre de Notifications) pour utiliser cette bibliothèque au lieu de HTML dupliqué à la main. 

- Suppression des 4 fonctions de compatibilité temporaires ( `gauge` , `trendArrow` , `kpiCardHTML` , `statusPill` ) introduites au Livrable 1, tous les appels passant 

- désormais directement par `Components` . 

### Bugs corrigés 

Aucun bug fonctionnel corrigé à ce stade (livrable de pure modularisation). 

- Une régression a été introduite puis corrigée avant livraison durant le développement : imbrication carte-dans-carte sur 3 vues (RH, Garantie, Finance) lors de la première extraction du composant tableau — détectée par test de non-régression automatisé, corrigée par ajout d'un paramètre `style` au primitif `card()` . 

### Refactoring 

- 7 tableaux `<table class="data">` dupliqués → 1 seul générateur 

- ( `Components.table` ), utilisé à 5 endroits ; 2 cas légitimement laissés hors composant (occurrence unique, ou génération dynamique côté Timeline). 

- 15 blocs `alert-row` écrits à la main → `Components.alertRow` / `alertList` , réutilisés à 7 endroits. 

- 8 cartes à valeur unique dupliquées → `Components.statCard` , réutilisé 12 fois. 

- 3 blocs "jauge centrée" dupliqués (Home, RH, KPI Center) → `Components.gaugeBlock` , un seul générateur. 

- 40 wrappers de carte écrits à la main → convergent progressivement vers le seul primitif `Components.card()` . 

### Décisions importantes 

- Règle d'architecture adoptée pour la suite : un motif visuel n'est promu en composant que s'il se répète au moins 2 fois (évite la sur-ingénierie). 

- Validation de non-régression réalisée par comparaison automatisée du contenu rendu de chaque vue (avant/après), plutôt que par relecture visuelle seule — méthode à reconduire pour le Livrable 3. 

- Quelques homogénéisations mineures et volontaires ont été actées (ex : légende de jauge unifiée à 11.5px partout, alignement flex des listes) — documentées dans le rapport technique, aucune n'altère la lisibilité ni la hiérarchie visuelle. 

## — [v3.0 Livrable 3 "Finalisation"] 

Date : Session 6 (après la séquence de planification stratégique Étape 1 à ADR) 

### Modifications 

Délégation d'événements : recherche globale, filtres de notifications, sélection Timeline — un seul écouteur par fonctionnalité, attaché une fois, au lieu d'un attachement par élément répété à chaque rendu. 

- Registre de graphiques ( `chartRegistry` + `mountChart()` ) : toute instance Chart.js est détruite avant recréation sur le même canvas. Échappement HTML systématique dans `Components` ( `escapeHtml()` ), avec option `raw:true` explicite par colonne de tableau pour le HTML volontaire (badges de 

- statut). 

### Bugs corrigés 

Aucun bug fonctionnel actif corrigé (les 3 chantiers étaient des dettes techniques identifiées, pas des bugs constatés en usage). 

- Correction d'une entité HTML pré-échappée ("objectif < 5%") qui aurait produit un double-échappement une fois `statCard` sécurisé par défaut. 

### Refactoring 

- Suppression des réattachements de listeners à chaque `renderAll()` (timeline, notifications) au profit d'une délégation unique posée dans `init()` . `Components.table` accepte désormais un attribut `raw` par colonne, appliqué aux 3 

- colonnes qui retournent du HTML volontaire (Garantie, RH, Administration). 

### Décisions importantes 

- Le Livrable 3 a été complété avant le démarrage de KPI-0 plutôt que fusionné avec KPI4 (Option 1 retenue) — cf. ADR-017. 

- Validation de non-régression réalisée par comparaison automatisée L2 → L3 sur les 21 vues, plus tests fonctionnels ciblés sur les 3 mécanismes modifiés (délégation, mémoire graphique, échappement). 

## [Étape 5 — Livrable KPI-0 "Peuplement du Repository"] 

Date : Session 7 

### Modifications 

Ajout d'une couche de données granulaires conforme au Data Model : 17 collections (Concession, Postes, Techniciens, Conseillers, Fournisseurs, Pièces, Clients, Véhicules, RendezVous, Devis, OrdreReparation, Intervention, LignePiece, TempsMainOeuvre, ControleQualite, Garantie, Facture). 

Génération déterministe via PRNG à seed fixe (mulberry32) — même jeu de données à chaque chargement, condition posée pour la vérifiabilité du futur KPI Engine. Repository étendu avec 17 nouvelles méthodes d'accès, sans toucher aux méthodes existantes. 

### Bugs corrigés 

Écart de génération détecté en cours de développement : le nombre d'OR réellement créés était inférieur à la cible validée (15-20/semaine) car le taux de refus de devis n'était pas compensé. Corrigé par une boucle génératrice qui continue jusqu'à atteinte exacte du volume cible. 

### Refactoring 

Aucun — livrable additif pur, aucune ligne des 21 vues existantes modifiée. 

### Décisions importantes 

Coexistence confirmée avec `REPORTS` : ces données n'alimentent encore aucune vue, elles préparent les Livrables KPI-1 et suivants. 

- Volumétrie finale : 16/18/17 OR sur S1/S2/S3 (conforme à la cible validée), 30 clients, 35 véhicules, 6 techniciens, 3 conseillers. 

Intégrité référentielle vérifiée automatiquement (0 erreur sur l'ensemble des relations inter-entités) et non-régression confirmée (0 diff structurel sur les 21 vues existantes). 

## [Étape 5 — Livrable KPI-1 "Cœur du moteur, 2 KPI pilotes"] 

Date : Session 7 (suite) 

### Modifications 

Interface d'exécution unique ( `KPIEngine.calculate` ), Extracteur 

- ( `kpiExtraireDonnees` ), Calculateur/Agrégateur ( `kpiCalculerAgregation` ) — périmètre restreint à 2 KPI pilotes : "Délai moyen de prise de RDV", "Nombre d'OR". 

- `KPI_DEFINITIONS` : format déclaratif simple (collection source, filtre, type 

- d'agrégation). 

### Vérifications 

Valeurs identiques à un contrôle manuel indépendant (calcul recalculé à la main sur les données de KPI-0). 

Déterminisme confirmé (deux appels successifs strictement identiques). 

- Cas limites gérés explicitement : donnée insuffisante → `null` (jamais `NaN` ), KPI inconnu → erreur explicite (jamais un plantage silencieux). Non-régression : 0 diff structurel sur les 21 vues existantes. 

## [Étape 5 — Livrable KPI-2 "Seuils, traçabilité, persistance"] 

Date : Session 7 (suite) 

### Modifications 

- Évaluateur de seuils ( `kpiEvaluerStatut` ), Traceur de provenance 

- ( `kpiResoudreSourcesReelles` ), Écrivain de résultats ( `kpiEcrireResultat` ) — `KPIValue` devient une donnée réellement persistée et historisée. 

- Règle de recalcul (ADR-015) implémentée : recalcul automatique, pas de duplication, horodatage de recalcul conservé. 

### Vérifications 

Persistance sans duplication après recalcul (ID et date de création d'origine préservés). Provenance : drill-down vérifié jusqu'aux enregistrements sources exacts (ADR-010). Statuts de seuil cohérents avec les valeurs calculées (contrôlé manuellement). Non-régression : 0 diff structurel sur les 21 vues existantes. 

## [Étape 5 — Livrable KPI-3 "Scheduler"] 

Date : Session 7 (suite) 

### Modifications 

- `Scheduler` : premier appelant réel de l'interface d'exécution unique (ADR-008), sans 

- infrastructure de planification réelle construite (non pertinente en fichier HTML autonome sans backend). 

- Cycle hebdomadaire simulé déclenché automatiquement au chargement, peuplant l'historique des 3 semaines disponibles. 

### Vérifications 

Historique peuplé automatiquement sans appel manuel. 

- Déterminisme confirmé sur valeur/statut/provenance entre deux chargements indépendants (seul l'horodatage varie naturellement). 

- Non-régression : 0 diff structurel sur les 21 vues existantes. 

[Étape 5 — Correctif KPI-2/KPI-3 : concessionId et contexte auteur] 

#### Date : Session 8 

### Modifications 

- `KPIValue` porte désormais `concessionId` (clé de dédoublonnage étendue) et `creePar` (contexte auteur minimal, défaut `'system'` ). `getValue` / `getHistory` acceptent un filtre optionnel par concession. `Scheduler.runAll` transmet `concessionId` (défaut : la concession existante) ; `runCycleHebdomadaire` inchangé. `KPIEngine.calculate` accepte un paramètre `contexte` optionnel, propagé à 

- l'écriture. 

### Bugs corrigés 

- Incohérence structurelle : `KPIValue` était la seule structure du KPI Engine sans `concessionId` , alors que ce champ est déjà porté par la quasi-totalité des autres 

- entités. 

### Décisions importantes 

Les deux ajouts ont été acceptés sur leurs mérites techniques propres (coût quasi nul, cohérence ou besoin plausible), pas sur la prémisse — inexacte — qu'ils auraient déjà été validés comme besoins du projet. Voir ADR-019 et ADR-020 pour la précision de gouvernance apportée. 

KPI-4 reste en attente : le blocage signalé avant ce correctif (incohérence entre les semaines narratives de `REPORTS` et les semaines S1/S2/S3 du KPI Engine) n'est pas résolu par ce correctif et attend toujours un arbitrage. 

### Vérifications 

Tests fonctionnels ciblés : dédoublonnage par concession, non-écrasement entre concessions différentes, préservation de `calculeLe` / `creePar` au recalcul, valeur par défaut `'system'` en l'absence de contexte — tous conformes. Non-régression : 0 diff structurel sur les 21 vues existantes. 

## [Pivot — Étape 1 backend : traduction du Data Model en schéma PostgreSQL] 

Date : Session 9 

### Modifications 

Nouveau schéma relationnel ( `APEX_schema.sql` ) : 26 entités du Data Model traduites en 30 tables PostgreSQL, avec contraintes CHECK/UNIQUE/FK réelles remplaçant les vérifications manuelles faites en JavaScript à KPI-0. 

6 écarts documentés entre modèle conceptuel et schéma relationnel (cf. ADR-021 et `APEX_Backend_Migration_Notes.md` ). 

### Décisions importantes 

KPI-4 est abandonné, pas reporté : le blocage signalé (incohérence narrative REPORTS / S1-S3) devient sans objet avec la bascule vers des données réelles. 

Le fichier HTML existant (jusqu'à KPI-3 corrigé) n'est ni supprimé ni modifié : il reste la référence du Data Model et de la logique métier pendant la transition. Précision de gouvernance apportée (ADR-022) sur la présentation de l'ambition produit — voir ADR pour le détail. 

Limite assumée de cette session : schéma conçu et testé localement (PostgreSQL local, sandbox) — aucun déploiement réel sur Supabase/Render effectué, ces actions nécessitant l'intervention directe d'Abdeljalil sur ces plateformes. 

### Vérifications 

Schéma exécuté avec succès sur un vrai PostgreSQL 16 (30 tables, 4 index, 0 erreur). Jeu de données test inséré avec succès (13 enregistrements) ; 3 tests négatifs délibérés (doublon, statut invalide, FK inexistante) tous correctement rejetés par les contraintes. 

## À venir 

### [Pivot backend — étape suivante] — en attente de cadrage 

Portage du KPI Engine (Extracteur/Calculateur adaptés au critère JSON et aux dates réelles), puis API FastAPI, puis authentification — chantiers séparés, un à la fois, non commencés. 

## [Orientations produit — Recommendation, données 

## internes/externes, synchronisation ERP] 

Date : Session 10 

### Modifications 

Aucune — documentation uniquement (ADR-023, ADR-024, ADR-025). Aucun code, aucun schéma modifié. 

### Décisions importantes 

Confirmation d'ADR-022 reçue et actée sans modification. 

- Couche `Recommendation` documentée comme extension distincte du KPI Engine, jamais une modification de son cœur. 

- Distinction actée entre données internes (ERP, quasi temps réel, isolation stricte) et données externes (marché, mensuel/trimestriel, mutualisation possible) — avec une question ouverte non résolue sur l'unité d'isolation ( `Concession` vs une future entité "Compte Client"). 

- Stratégie de synchronisation ERP actée : polling incrémental par défaut, webhooks en complément ponctuel. 

### Tensions signalées (ni résolues ni ignorées) 

- `Recommendation` recoupe conceptuellement le module "AI Advisor" existant (déjà 

- identifié dans l'audit v2.0 comme nécessitant une clarification) — à réconcilier au moment de l'implémentation plutôt que de construire deux systèmes parallèles. Le schéma de l'Étape 1 isole par `concession_id` sans entité parente "Compte Client" — à trancher avant la connexion du premier ERP réel. 

- Le polling incrémental constituera, une fois construit, un véritable producteur d'événements — ce sera le signal légitime pour rouvrir la question d'un KPI Engine Event-Driven, écartée à l'Étape 4 faute d'un tel producteur. 

### Vérifications 

Aucune : livrable documentaire pur, aucun code modifié, non-régression sans objet. 

## — [Pivot backend Organisation : fermeture d'ADR-024] 

Date : Session 11 

### Modifications 

- `schema.sql` : nouvelle table `organisations` ; `concessions.organisation_id` (NOT 

- NULL, FK) ; index `idx_concessions_organisation` . Aucune autre table modifiée — isolation par organisation déduite par jointure, pas dupliquée. 

### Décisions importantes 

Referme la question ouverte d'ADR-024 : l'isolation entre clients payants d'APEX se fait désormais au niveau `organisation_id` , `concession_id` restant la granularité interne à un même client. 

- Dénormalisation de `organisation_id` sur les autres tables envisagée puis explicitement écartée (aucune donnée de charge réelle ne la justifie à ce stade). Row-Level Security sur `organisation_id` notée comme mécanisme prévu pour la phase API/Auth à venir, non implémentée ici. 

### Vérifications 

Schéma recréé sur PostgreSQL local : 31 tables, 0 erreur. 

- Jeu de données test étendu (organisation + concession rattachée) ; 4 tests négatifs (dont le nouveau, spécifique à `organisation_id` ) tous correctement rejetés par les contraintes. 

Aucune régression sur les 30 tables et contraintes déjà validées à l'Étape 1. 

## [Pivot backend — Étape 2 : portage du KPI Engine vers Python] 

Date : Session 12 

### Modifications 

- Nouveau module `kpi_engine_py/` : `db.py` (connexion + réflexion SQLAlchemy), `extracteur.py` , `calculateur.py` , `evaluateur.py` , `ecrivain.py` , `engine.py` 

- (interface d'exécution unique). 

- Jeu de données de test enrichi ( `APEX_enrichir_test.sql` ) : 5 RDV et 3 OR supplémentaires, seconde KPIDefinition pilote ( `kpi-nombre-or` ) ajoutée à la base de test. 

### Bugs corrigés 

`TypeError` réelle détectée pendant le test ( `Decimal` PostgreSQL vs `float` Python dans l'évaluateur de seuils) — corrigée par conversion explicite. Un cas invisible côté JavaScript, détecté uniquement grâce au test réel contre PostgreSQL. 

### Décisions importantes 

Bibliothèque d'accès aux données : SQLAlchemy Core avec réflexion automatique du schéma (pas de modèle Python dupliquant `APEX_schema.sql` , pas de psycopg2 brut) — voir ADR-027. 

- Écart signalé, non corrigé silencieusement : le schéma ne déclare pas quelle colonne de date sert au filtrage de période par collection source ; résolu provisoirement par une correspondance codée en dur, signalée comme limite à lever dans une prochaine étape ( `kpi_definitions.date_champ_periode` ). 

- Écriture des résultats appuyée directement sur la contrainte UNIQUE existante via `INSERT ... ON CONFLICT DO UPDATE` , conformément à la demande de ne pas la 

- contourner. 

### Vérifications 

Exécution réelle contre PostgreSQL local (pas une relecture) : les 2 KPI pilotes calculés par le module Python correspondent exactement à un contrôle SQL manuel indépendant. 

- Test de recalcul (ADR-015) : `cree_le` / `cree_par` préservés, `recalcule_le` mis à jour, aucun doublon créé (vérifié par comptage direct des lignes `kpi_values` ). Cas limite testé : version de KPIDefinition inexistante correctement rejetée par une erreur explicite. 

## [5 décisions consolidées — méthode et produit, avant Étape 3] 

Date : Session 13 

### Modifications 

- `APEX_schema.sql` : ajout de `kpi_definitions.date_champ_periode` (TEXT NOT 

- NULL). 

- `kpi_engine_py/extracteur.py` : dictionnaire codé en dur retiré, lecture depuis la 

- base. 

- `APEX_schema_test.sql` / `APEX_enrichir_test.sql` : mis à jour en conséquence. 

### Décisions importantes 

- Nouvelle consigne permanente : vérification de reprise de session en début de chaque session (état réel vs rapporté), appliquée dès cette session — aucun écart trouvé. ADR-028 : exigence de débit configurable par client pour le futur ERPAdapter (complément ADR-025), documentaire. 

- ADR-029 : `Recommendation` remplace `AI Advisor` , ferme la question ouverte d'ADR023. 

- ADR-030 : confirmation sans changement de la décision ADR-021 (trigger `historique_statut` différé). 

ADR-031 : ferme l'écart signalé à ADR-027. 

### Vérifications 

- Schéma reconstruit intégralement (31 tables — ajout d'une colonne, pas d'une table), 0 erreur. 

- Les 2 KPI pilotes recalculés produisent des valeurs strictement identiques à avant le correctif — confirmé : changement de représentation, pas de comportement. Test de recalcul (ADR-015) toujours conforme après le correctif. 

## [Pivot backend — Étape 3 : API FastAPI] 

Date : Session 14 

### Modifications 

Nouveau dossier `api/` : `main.py` (5 routes), `schemas.py` (modèles Pydantic). Nouveau module `kpi_engine_py/provenance.py` : résolution des sources d'une KPIValue (absent de l'Étape 2, signalé et ajouté ici). 

### Bugs corrigés 

`ResponseValidationError` réelle détectée pendant le test : types `UUID` PostgreSQL non compatibles avec des champs Pydantic déclarés `str` . Corrigée en déclarant les champs concernés en type `UUID` . 

### Décisions importantes 

Gestion de connexion : engine + métadonnées réfléchies créés une seule fois au démarrage (lifespan), connexion par requête via `Depends` — voir ADR-032. Écart signalé : la fonction de résolution de provenance n'avait pas été portée à l'Étape 2 (hors périmètre à l'époque) ; ajoutée maintenant, pas supposée déjà faite. 

- Aucune modification de `kpi_engine_py` existant : l'API route et sérialise uniquement. 

### Vérifications 

Test réel (FastAPI TestClient, pas de mock) contre PostgreSQL local : les 2 KPI pilotes calculés via HTTP, historique consulté, provenance résolue jusqu'aux enregistrements sources réels. 

- Confirmation qu'ADR-015 (recalcul, préservation `cree_par` / `cree_le` ) tient à travers la couche HTTP. 

- Cas d'erreur testés : KPI inconnu → 404 explicite, KPIValue inexistante → 404 explicite (pas de 500 opaque). 

## [Déploiement réel — Supabase] 

Date : Session 15 

### Modifications 

- `kpi_engine_py/db.py` : DSN lu depuis la variable d'environnement `DATABASE_URL` 

- (repli local si absente) — plus de mot de passe codé en dur, permet de pointer vers Supabase sans modifier le code. 

### Décisions importantes 

- Schéma et jeux de données de test déployés avec succès sur une instance Supabase réelle, exécutés directement par Abdeljalil (mon bac à sable ne peut pas atteindre `supabase.co` — confirmé par diagnostic réseau, `x-deny-reason:` 

- `host_not_allowed` ). 

Mot de passe partagé en clair dans la conversation changé immédiatement après usage, sur recommandation donnée avant l'exécution. Voir ADR-033 pour le détail complet, y compris ce qui reste à vérifier. 

### Vérifications 

- Confirmé par Abdeljalil : les 3 scripts SQL ( `schema.sql` , `test_data.sql` , `enrichir_test.sql` ) s'exécutent sans erreur sur Supabase ; données vérifiées 

- visuellement dans le Table Editor. 

Non confirmé à ce stade : `test_engine_reel.py` et `test_api_reel.py` pas encore exécutés contre Supabase — le moteur KPI et l'API restent à vérifier sur cette instance réelle avant de considérer l'étape totalement close. 

## [Fermeture de la vérification Supabase — moteur KPI et API] 

Date : Session 16 

### Modifications 

- Aucune modification de code ou de schéma — changement de la chaîne de connexion utilisée (Session Pooler Supabase au lieu de l'hôte direct). 

### Bugs corrigés 

Échec de connexion réel rencontré : hôte Supabase direct résolu en IPv6 sans route IPv4 disponible côté client. Résolu en utilisant le Session Pooler (IPv4) de Supabase. 

### Décisions importantes 

Ferme définitivement la limite laissée ouverte à ADR-033 : le moteur KPI et l'API sont désormais confirmés fonctionnels contre l'instance Supabase réelle, pas seulement le schéma et les données. 

- Point à retenir pour tout déploiement futur : utiliser le Session Pooler Supabase, pas l'hôte direct, en contexte réseau IPv4 uniquement. 

### Vérifications 

- `test_engine_reel.py` : tous les tests passent contre Supabase réel (recalcul ADR- 

- 015 inclus). 

- `test_api_reel.py` : tous les tests passent contre Supabase réel (routes GET/POST, 

- cas d'erreur 404 inclus). 

[Pivot backend — Étape 4 : authentification JWT + autorisation par organisation] 

Date : Session 17 

### Modifications 

- Nouveau module `api/auth.py` : vérification JWT Supabase ( `SUPABASE_JWT_SECRET` lu depuis l'environnement), autorisation par organisation. 

- `api/main.py` : les 5 routes exigent un token Bearer valide ; `auteur` retiré du schéma 

- de requête ( `cree_par` vient exclusivement du token). `APEX_schema.sql` : nouvelle table `membres_organisation` (ADR-035), liaison 

- utilisateur Supabase Auth ↔ organisation. 

- `.env.example` ajouté (gabarit sans valeurs réelles). 

### Décisions importantes 

ADR-035 (table `membres_organisation` ) rédigée avant construction, pas après. ADR-036 : authentification et autorisation validées en local ; confirmation contre Supabase réel encore attendue. 

- Consigne de sécurité appliquée : aucun secret réel (mot de passe, JWT Secret) n'a été partagé en clair dans la conversation ni codé en dur dans un fichier — uniquement via variables d'environnement. 

### Vérifications 

- Test complet local (PostgreSQL + JWT de test signé localement) : 401 sans token, 401 token invalide, 200 token valide, 403 sur une concession hors organisation, recalcul préservant `cree_par` d'origine (ADR-015 confirmé via HTTP), création attribuant correctement `cree_par` à l'identité du token. 

- Écart non bloquant noté : un token de test expiré entre deux tours de session a été correctement rejeté (comportement attendu, pas un défaut) — régénéré et retest réussi. 

## — [Correctif migration JWKS/ES256 (ADR-037)] 

Date : Session 18 

### Modifications 

`api/auth.py` réécrit : vérification via JWKS/ES256 ( `PyJWKClient` ), plus de `SUPABASE_JWT_SECRET` . 

- `.env.example` : `SUPABASE_JWT_SECRET` remplacé par `SUPABASE_URL` . 

Nouvel outil de test `mock_jwks_server.py` : serveur JWKS local avec vraie paire de clés EC P-256, pour tester le mécanisme ES256 sans accès réseau à `supabase.co` . 

### Bugs corrigés 

Aucun bug de code : `test_engine_reel.py` avait déjà réussi contre Supabase réel ; `test_api_reel.py` échouait car le projet Supabase d'Abdeljalil est migré vers les clés asymétriques, sans repli HS256 possible (confirmé Dashboard). 

### Décisions importantes 

Voir ADR-037 : choix motivé aussi bien par la contrainte réelle du projet que par une sécurité objectivement meilleure (pas de secret partagé à protéger côté serveur de vérification). 

Base de données locale reconstruite avant chaque nouveau test pour garantir un résultat déterministe, indépendant des runs précédents. 

### Vérifications 

Suite de tests complète repassée en local avec le nouveau mécanisme ES256/JWKS : tous les cas (401/403/200/404, ADR-015, ADR-035) toujours conformes. Reste à confirmer par Abdeljalil : `test_api_reel.py` contre le vrai JWKS Supabase (le mécanisme local utilise une clé de test équivalente, pas la vraie clé Supabase). 

## [Étape 4 — clôture officielle] 

Date : Session 19 

### Modifications 

Aucune — confirmation finale uniquement. 

### Décisions importantes 

ADR-038 : suite de tests complète ( `test_engine_reel.py` + `test_api_reel.py` ) confirmée par Abdeljalil contre l'infrastructure Supabase réelle (base + JWKS + token réels, aucun composant simulé). 

Étape 4 officiellement close. Chaîne complète validée en conditions réelles : Data Model → moteur KPI Python → API FastAPI → authentification/autorisation. 

### Vérifications 

Confirmé par Abdeljalil : "TOUS LES TESTS PASSÉS CONTRE SUPABASE RÉEL (base + JWKS + token réels)". 

## [Correction RLS + prototype frontend de validation de chaîne] 

Date : Session 20 

### Modifications 

- `verifier_rls_anon.py` (nouveau) : vérification indépendante RLS via clé 

- anon/PostgREST. 

- `frontend_prototype/index.html` (nouveau) : page unique, flux réel Supabase Auth + 

- appel API + affichage résultat, séparée du prototype HTML existant. 

- `api/main.py` : CORS activé ( `allow_origins=["*"]` , dette de sécurité assumée pour 

- ce stade, à restreindre avant production). 

- `test_prototype_chaine.py` (nouveau) : validation de la chaîne API + CORS via 

- TestClient (POST + preflight OPTIONS). 

### Correction 

Étape précédente avait présenté à tort l'activation RLS comme une action à venir : elle était déjà faite depuis plusieurs semaines par Abdeljalil, indépendamment de moi. Corrigé dans ADR-039. 

### Décisions importantes 

- Priorisation actée par Abdeljalil : prototype frontend avant policies RLS fines et avant ERP réel. 

- Difficultés d'orchestration de processus en arrière-plan dans le bac à sable (uvicorn ne survit pas entre plusieurs appels d'outils) — contournées en testant la chaîne API + CORS via TestClient in-process plutôt qu'un vrai serveur réseau, sans perte de couverture réelle (même stack ASGI, même middleware CORS traversé). 

### Vérifications 

Chaîne API + CORS validée localement (statut 200, en-tête CORS présent, preflight OPTIONS 200). 

- Non testé depuis ce bac à sable (limite réseau) : connexion Supabase Auth réelle dans un vrai navigateur — à confirmer par Abdeljalil. 

## [Confirmation finale — RLS prouvé, chaîne complète validée] 

Date : Session 21 

### Modifications 

Aucune — confirmation finale uniquement. 

### Décisions importantes 

ADR-040 : RLS deny-by-default prouvé par preuve indépendante (clé anon, 200+0 ligne sur tables non vides, confirmé par Supabase Dashboard). Prototype frontend validé de bout en bout avec navigateur réel, Auth réel, API réelle. 

Confirmation notable : ADR-015 (recalcul, préservation de paternité) prouvé fonctionnel à travers la chaîne HTTP complète réelle, pas seulement en local. 

- Chaîne complète confirmée : Auth réel → API réel → RLS confirmé → Frontend confirmé. 

### Vérifications 

- `verifier_rls_anon.py` : refus confirmé sur 5 tables (200+0 ligne, tables non vides 

- vérifiées manuellement). 

- Prototype frontend : connexion réelle + appel API réel + résultat HTTP 200 correct, `cree_par` d'origine préservé malgré changement d'utilisateur connecté. 

## [Report RLS fine + CORS, test de régression compensatoire] 

Date : Session 22 

### Modifications 

- `test_regression_autorisation.py` (nouveau) : analyse statique (AST) de `api/main.py` , vérifie que toute route référençant `concession_id` appelle `_exiger_acces_organisation` . 

### Décisions importantes 

- ADR-041 : RLS fine et restriction CORS reportées sous critère corrigé — "avant tout nouveau chemin d'accès externe via clé anon/authenticated directe", explicitement PAS "avant connexion ERP" (l'ERPAdapter utilisera un rôle de service fiable, ne change pas le modèle de menace). 

- Mesure compensatoire actée et documentée, pas un oubli : le test de régression protège contre l'omission humaine future à un coût très inférieur à RLS fine complète. 

### Vérifications 

Test exécuté sur le code actuel : 3 routes conformes, 0 omission. 

Preuve que le test fonctionne réellement : vérification supprimée artificiellement d'une route (test du test lui-même) → échec correctement détecté ; code restauré → test repasse au vert. 

## [Correctif de portabilité — test_regression_autorisation.py] 

Date : Session 23 

### Bugs corrigés 

Chemin absolu codé en dur ( `/home/claude/apex_backend/api/main.py` , propre au bac à sable) rendant le script inutilisable sur la machine d'Abdeljalil (Windows) — relevé par Abdeljalil. 

### Modifications 

Chemin par défaut désormais calculé relativement à l'emplacement du script ( `Path(__file__).resolve().parent` ), plus une option `--main-path` pour le surcharger explicitement. 

### Vérifications 

- Revérifié dans 3 configurations : depuis le dossier du script, depuis un dossier différent, avec `--main-path` explicite — les trois fonctionnent identiquement. 

## — [ERPAdapter AtlasCom initial lecture + transformation] 

Date : Session 23 (suite) 

### Modifications 

- `erp_adapters/atlascom_adapter.py` (nouveau) : lit `article.dbf` (cp850), 

- transforme vers un format proche de `pieces` , selon les correspondances de champs confirmées par Abdeljalil sur données réelles. Aucune écriture en base à ce stade. 

- `creer_dbf_test.py` (outil de test) : génère un fichier DBF synthétique réel 

- (bibliothèque `dbf` ) pour valider le code sans accès au partage réseau local d'Abdeljalil. 

### Décisions importantes 

- ADR-042 : les 3 correspondances de champs ( `QTESTOCK` → `stock` , 

- `PRIX1` → `prix_catalogue` , `CODE` → `code_externe` ) confirmées et closes sur données 

- AtlasCom réelles (5 codes distincts, vérification croisée directe dans l'interface AtlasCom). 

- Enseignement notable : un prix qui semblait élevé (45 000 MAD) s'est révélé correct — `article.dbf` contient aussi de l'équipement d'atelier lourd (volucompteurs), pas 

- uniquement des pièces détachées. Le mapping était juste ; l'hypothèse implicite sur la nature du catalogue était incomplète. 

- Note ouverte, documentée et non tranchée : la diversité des types d'articles (pièces consommables vs équipement lourd) questionne si `pieces` est le bon cadre unique — 

différé à un échantillon de données plus large, pas décidé sur un seul cas. 

- Lacune de schéma identifiée et signalée, pas corrigée silencieusement : `pieces` n'a aucun identifiant externe stable. Proposition ( `code_externe TEXT` ) documentée, non appliquée à APEX_schema.sql sans validation explicite. 

- `COFOURN` (fournisseur) transmis tel quel ; nécessitera une table de correspondance 

- avant toute écriture réelle, non construite à ce stade. 

### Vérifications 

Adaptateur validé indépendamment par Abdeljalil (ré-exécution locale, résultat identique), puis contre les vraies données AtlasCom sur 5 codes distincts avec vérification croisée directe dans l'interface AtlasCom — pas une simple relecture de mapping théorique. 

## — [ADR-043 code_externe + fournisseurs_mapping_externe] 

Date : Session 24 

### Modifications 

- `APEX_schema.sql` : `pieces.code_externe TEXT` (nullable) ajouté. Nouvelle table `fournisseurs_mapping_externe` ( `code_externe` , `source_erp` , `concession_id` , `fournisseur_id` , UNIQUE sur les 3 premiers) — volontairement vide. 

### Décisions importantes 

Ferme les 2 points ouverts d'ADR-042 : proposition `code_externe` appliquée ; structure de correspondance fournisseurs créée (sans données, chantier séparé à venir). 

- `code_externe` nommé génériquement (pas `code_atlascom` ) : réutilisable pour tout 

- futur ERP. 

- Observation signalée, pas corrigée : `fournisseurs` reste une table globale (pas de `concession_id` ), tandis que la nouvelle table de correspondance est scopée par 

- concession — cohérent avec le schéma existant, documenté pour ne pas être redécouvert par surprise. 

- Périmètre strictement respecté : aucune exploration de `bonlivra` / `boncom` , aucune écriture réelle dans `pieces` — chantiers séparés, non commencés. 

### Vérifications 

Schéma reconstruit intégralement sur PostgreSQL local (pas une relecture) : 33 tables, 0 erreur. 

- `\d pieces` confirme `code_externe` en `TEXT` , nullable. 

- `\d fournisseurs_mapping_externe` confirme la structure attendue. 

`SELECT count(*) FROM fournisseurs_mapping_externe` confirme 0 ligne, comme demandé. 

