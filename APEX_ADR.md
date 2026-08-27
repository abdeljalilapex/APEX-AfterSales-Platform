# — APEX_ADR.md Architecture Decision Records 

## Registre officiel des décisions d'architecture du projet APEX 

Convention adoptée : un seul fichier, entrées numérotées chronologiquement (ADR-001, ADR-002...), jamais réécrites — une décision remplacée reçoit un nouveau numéro et l'ancienne entrée passe au statut Remplacé avec renvoi vers la nouvelle. Chaque entrée reste volontairement courte : elle pointe vers le document de détail, elle ne le duplique jamais. 

Format de chaque entrée : Décision · Contexte (1-2 phrases) · Justification · Documents impactés · Statut. 

### — ADR-001 Repository comme point d'accès unique aux données 

- Décision — Toute lecture de données passe exclusivement par une couche `Repository` ; aucune autre partie du code ne lit les structures de données brutes directement. 

- Contexte — APEX v2.0 avait atteint la limite d'un fichier unique sans séparation entre données, logique et présentation (audit de Design Review). 

- Justification — Seul point à réécrire le jour d'une migration vers un vrai backend, sans toucher au reste de l'application. 

- Documents impactés — Code source (Livrable 1, refactoring v3.0). 

Statut — Validé. 

### — ADR-002 État de navigation centralisé (AppState) 

- Décision — Les variables globales dispersées (semaine active, sélection de comparaison) sont remplacées par un magasin d'état unique et minimal. 

- Contexte — Incohérences potentielles entre parties de l'application dépendant du même état mais le lisant/modifiant indépendamment. 

- Justification — Simplicité choisie délibérément (pas de système de souscription complet) : suffisant à l'échelle actuelle, évite la sur-ingénierie. 

- Documents impactés — Code source (Livrable 1, refactoring v3.0). 

- Statut — Validé. 

### — ADR-003 Bibliothèque de composants à deux étages, règle des "2 occurrences" 

- Décision — Un seul primitif de carte 

- ( `Components.card` ) sous-tend tous les composants composites ; un motif visuel n'est promu en composant que s'il se répète au moins deux fois. 

- Contexte — Duplication mesurée et quantifiée dans le code (7 tableaux, 15 blocs d'alerte, 8 cartes statistiques 

réécrits à la main). 

- Justification — Une seule modification suffit pour changer l'apparence de tous les éléments d'un même type ; évite de créer des composants prématurés non justifiés par un usage réel. 

- Documents impactés — Code source (Livrable 2, refactoring v3.0). 

Statut — Validé. 

### — ADR-004 Le Business Process est la source de 

### vérité du Data Model 

- Décision — Chaque entité du Data Model doit être reliée explicitement à une ou plusieurs étapes du Business Process ; aucune entité n'est ajoutée sans cette justification. 

- Contexte — Risque identifié de construire un modèle de données comme "liste d'entités imaginées" plutôt que comme reflet du métier réel. 

- Justification — Garantit que le modèle reste ancré dans un besoin réel, pas dans une anticipation technique. 

#### Documents impactés — 

- `APEX_Business_Process_Analysis.md` , 

- `APEX_Data_Model.md` . 

Statut — Validé. 

### — ADR-005 Ajout de Concession, Poste, 

### Fournisseur ; rejet d'Equipment 

- Décision — Trois entités ajoutées au Data Model 

- (dimension transversale peu coûteuse à poser 

maintenant) ; une entité (suivi détaillé des équipements physiques) explicitement écartée, faute de justification dans le Business Process. 

- Contexte — Revue d'architecture complémentaire postconception initiale du Data Model. 

- Justification — Coût asymétrique : 

- Concession/Poste/Fournisseur peu coûteux maintenant, très coûteux en rattrapage ; Equipment non justifié par aucune étape validée. 

- Documents impactés — `APEX_Data_Model.md` . 

- Statut — Validé. 

### — ADR-006 Séparation KPIDefinition / KPIValue 

- Décision — La définition d'un KPI (formule, seuils, stable) et son résultat calculé (fréquent, périodique) sont deux entités distinctes. 

- Contexte — Nécessité identifiée dès l'analyse 

- d'architecture initiale du KPI Engine (Étape 1). 

- Justification — Condition nécessaire pour ajouter un nouveau KPI sans jamais modifier le moteur de calcul lui-même. 

- Documents impactés — `APEX_Data_Model.md` , `APEX_KPI_Engine_Architecture.md` . 

- Statut — Validé. 

### — ADR-007 Architecture B retenue pour le KPI Engine (calcul planifié + stocké, définitions déclaratives simples) 

- Décision — Le moteur calcule à intervalles définis (ou sur événement métier), stocke les résultats, et les définitions de KPI restent de simples configurations plutôt que du code ou un langage de règles complexe. 

- Contexte — Quatre architectures comparées (calcul à la volée, planifié+stocké, DSL de règles riche, moteurs spécialisés par domaine). 

- Justification — Seule option cohérente avec 

- l'historisation déjà utilisée (Timeline) et avec le principe de simplicité ; les trois alternatives ont été explicitement écartées (sur-ingénierie ou incompatibilité avec l'existant). 

#### Documents impactés — 

- `APEX_KPI_Engine_Architecture.md` . 

Statut — Validé. 

### — ADR-008 Indépendance du moteur vis-à-vis de son mode de déclenchement 

- Décision — Le KPI Engine expose une interface 

- d'exécution unique ; il ne sait jamais si l'appel provient d'un Scheduler, d'un événement métier ou d'une future API. 

- Contexte — Discussion technique sur l'opportunité d'une architecture Event-Driven comme mécanisme principal du moteur. 

- Justification — Ajouter un futur mode de déclenchement ne demandera jamais de modifier le cœur du moteur, seulement d'écrire un nouvel appelant externe. 

#### Documents impactés — 

`APEX_KPI_Engine_Architecture.md` . 

Statut — Validé. 

### — ADR-009 KPI Versioning 

- Décision — `KPIDefinition` porte un numéro de 

- version ; chaque `KPIValue` référence la version exacte de la formule active au moment du calcul. 

- Contexte — Question posée : une révision future de formule doit-elle réinterpréter l'historique ou le préserver tel qu'il a été calculé ? 

- Justification — Coût d'anticiper quasi nul ; coût de ne pas anticiper potentiellement irrattrapable (impossible de reconstituer a posteriori quelle formule était active). 

#### Documents impactés — 

- `APEX_KPI_Engine_Architecture.md` uniquement (pas 

- le Data Model — cf. ADR-012). 

Statut — Validé. 

### — ADR-010 Provenance des données : drill-down 

### jusqu'aux identifiants sources 

- Décision — La traçabilité d'un KPI doit permettre de remonter jusqu'aux identifiants exacts des 

- enregistrements sources, pas seulement un compteur agrégé. 

- Contexte — Question posée : que répondre concrètement à "d'où vient ce chiffre ?". 

- Justification — Distingue un outil de pilotage crédible d'un outil dont les chiffres doivent être crus sur parole. 

#### Documents impactés — 

`APEX_KPI_Engine_Architecture.md` . 

Statut — Validé. 

### — ADR-011 Dépendances entre KPI calculés 

### écartées ; réutilisation de l'extracteur retenue 

- Décision — Un KPI ne dépend jamais du résultat calculé d'un autre KPI (pas de graphe de dépendances) ; plusieurs `KPIDefinition` peuvent en revanche référencer les mêmes données brutes extraites. 

- Contexte — Proposition d'un graphe de dépendances entre KPI (ex : Profitabilité dépendant de CA Atelier). 

- Justification — Un graphe de dépendances recréerait la même famille de risques que le DSL de règles déjà écarté (ADR-007) : ordre de recalcul, cycles, cascades — non justifié à l'échelle actuelle. 

#### Documents impactés — 

- `APEX_KPI_Engine_Architecture.md` . 

- Statut — Validé (différé — critère de réouverture documenté dans le document source). 

### — ADR-012 Principe des 3 niveaux : Business 

### Model / Architecture / Implémentation 

- Décision — Le Data Model n'évolue que si le Business Process évolue ; les décisions techniques des modules (KPI Engine, futurs modules) vivent dans leur propre document d'architecture jusqu'à leur implémentation réelle. 

- Contexte — Une métadonnée technique avait été ajoutée par erreur au Data Model alors qu'elle relevait 

- d'une décision d'architecture du KPI Engine. 

- Justification — Évite que le Data Model grossisse au gré des préoccupations techniques successives ; préserve sa valeur de document stable et strictement dérivé du métier. 

#### Documents impactés — 

`APEX_Gouvernance_Architecture.md` , 

- `APEX_Data_Model.md` (correction), 

- `APEX_KPI_Engine_Architecture.md` . 

- Statut — Validé. 

### — ADR-013 Indépendance vis-à-vis des systèmes externes (ERP/DMS) 

- Décision — Le cœur fonctionnel d'APEX ne dépend jamais d'un ERP, d'un DMS ou d'un constructeur particulier ; toute intégration future passe par une couche d'adaptation dédiée. 

- Contexte — Formalisation explicite d'une règle jusque-là implicite depuis ADR-001. 

- Justification — Cohérent avec le positionnement produit d'APEX (couche de pilotage, pas un ERP) ; empêche par avance un raccourci futur qui courtcircuiterait le Repository. 

#### Documents impactés — 

- `APEX_Gouvernance_Architecture.md` . 

- Statut — Validé. 

### — ADR-014 Adoption de la pratique ADR, fichier 

### unique 

- Décision — Les décisions d'architecture sont désormais enregistrées dans un registre unique ( `APEX_ADR.md` ), au format court standard de l'industrie, plutôt qu'un rapport narratif consolidé ou un dossier multi-fichiers. 

- Contexte — Recherche d'une méthode de suivi documentaire robuste à long terme, alors que les décisions étaient jusque-là tracées séparément dans chaque document. 

- Justification — Un rapport consolidé complet aurait dupliqué le contenu des historiques déjà présents dans chaque document (risque de double source de vérité) ; un dossier multi-fichiers ne se justifie qu'à partir d'un volume ou d'un contexte multi-contributeurs Git que nous n'avons pas encore. 

- Documents impactés — Ce document lui-même. 

- Statut — Validé. 

### — ADR-015 Recalcul automatique en cas de 

### correction d'une donnée source 

- Décision — Le KPI Engine recalcule automatiquement une `KPIValue` affectée par la correction d'une donnée source, sans système de notification séparé ; un horodatage de dernier recalcul est conservé directement dans `KPIValue` . 

- Contexte — Dernière décision ouverte de l'Étape 4 : silencieux vs notifié en cas de correction rétroactive d'une donnée. 

- Justification — Un mécanisme de notification dédié serait une infrastructure construite pour un besoin encore hypothétique ; l'horodatage donne une 

transparence minimale suffisante sans rien construire de plus qu'un champ. 

#### Documents impactés — 

`APEX_KPI_Engine_Architecture.md` . 

Statut — Validé. 

### — ADR-016 Fréquence de calcul par défaut 

### hebdomadaire 

- Décision — Le KPI Engine calcule par défaut selon un cycle hebdomadaire, aligné sur le cycle de rapport déjà utilisé dans APEX ; déclenchement événementiel possible en complément, sans infrastructure événementielle construite à ce stade. 

- Contexte — Dernière décision ouverte de l'Étape 4. 

- Justification — Cohérence avec l'usage existant d'APEX (rapports hebdomadaires) ; évite de fixer une fréquence arbitraire non alignée sur le rythme métier réel. 

#### Documents impactés — 

`APEX_KPI_Engine_Architecture.md` . 

- Statut — Validé. 

### — ADR-017 Clôture du Livrable 3 (Finalisation du refactoring v3.0) 

- Décision — Délégation d'événements (recherche, filtres de notifications, timeline), registre de graphiques avec destruction avant recréation, échappement HTML par défaut dans Components (avec option `raw:true` explicite pour le HTML volontaire). 

- Contexte — Dernier livrable du refactoring v3.0, resté ouvert depuis le Livrable 2, complété avant le démarrage de KPI-0 (Option 1 retenue plutôt que fusion avec KPI-4). 

- Justification — Cohérence avec les 3 objectifs déjà scopés au plan de refactoring initial ; ne pas empiler le KPI Engine sur des fondations connues comme incomplètes. 

- Documents impactés — Code source 

- ( `APEX_AutoPerf_Group_v3.0_L3.html` ), `APEX_CHANGELOG.md` . 

Statut — Validé. 

### — ADR-018 Clôture du Livrable KPI-0 (données granulaires) 

- Décision — Le Repository expose désormais 17 collections d'entités granulaires (Concession, Postes, Techniciens, Conseillers, Fournisseurs, Pièces, Clients, Véhicules, RendezVous, Devis, OrdreReparation, Intervention, LignePiece, TempsMainOeuvre, ControleQualite, Garantie, Facture), générées de façon déterministe (PRNG à seed fixe), en coexistence pure avec `REPORTS` . 

- Contexte — Premier livrable de la roadmap KPI Engine (Étape 5) : donner au futur moteur des données brutes réelles à calculer, conformément au Data Model validé. 

- Justification — Volumétrie validée (16/18/17 OR sur 3 semaines) atteinte exactement après correction d'un écart de génération (le taux de refus de devis réduisait le nombre d'OR sous la cible) ; intégrité référentielle 

vérifiée automatiquement (0 erreur sur l'ensemble des relations) ; aucune vue existante modifiée (0 diff structurel sur les 21 vues). 

Documents impactés — Code source 

- ( `APEX_AutoPerf_Group_v3.0_KPI0.html` ), `APEX_CHANGELOG.md` . 

Statut — Validé. 

### — ADR-019 Ajout de concessionId à KPIValue 

- Décision — `KPIValue` porte désormais `concessionId` ; la clé de dédoublonnage passe de `(kpiId, version, semaine)` à `(kpiId, version, semaine, concessionId)` ; `getValue` / `getHistory` acceptent un filtre optionnel par concession ; `Scheduler.runAll` transmet `concessionId` à `KPIEngine.calculate` . 

- Contexte — Un correctif signalé a relevé que `KPIValue` était la seule structure du KPI Engine sans 

- `concessionId` , alors que ce champ est déjà porté par 

- la quasi-totalité des autres entités (Postes, Techniciens, RendezVous, OrdreReparation...). 

- Justification — Cohérence avec un motif déjà établi ailleurs dans le code, pas une anticipation nouvelle : sans ce champ, deux concessions calculant le même KPI la même semaine s'écraseraient silencieusement l'une l'autre. Précision de gouvernance : contrairement à la formulation initiale du correctif signalé, ceci ne découle pas d'une "architecture multi-instance par client déjà actée" — aucun ADR ni document d'architecture n'a validé un tel besoin. La décision d'ajouter Concession (ADR-005) répondait à un objectif plus restreint (dimension transversale peu coûteuse à poser tôt). Le 

correctif est accepté sur la seule base de la cohérence technique constatée, pas sur la prémisse d'un besoin déjà validé. 

- Documents impactés — Code source uniquement (aucun document d'architecture à modifier : ce champ prolonge une décision déjà actée, ADR-005). 

- Statut — Validé. 

### — ADR-020 Ajout d'un contexte auteur minimal (creePar) à KPIValue 

- Décision — `kpiEcrireResultat` accepte un paramètre `contexte` optionnel ( `{ auteur }` ) ; `KPIValue` porte 

- un champ `creePar` , valant `'system'` par défaut en l'absence de contexte, `'scheduler'` pour les appels du Scheduler. 

- Contexte — Un correctif signalé a proposé ce champ en anticipation d'une future authentification. 

- Justification — Coût quasi nul (un champ, une valeur par défaut) pour un besoin futur plausible (traçer qui a déclenché un recalcul), sur le même raisonnement que celui qui a validé le KPI Versioning (ADR-009). Précision 

- de gouvernance : ici aussi, aucun document d'architecture existant ne mentionnait ce besoin avant le correctif signalé — ce n'est pas la correction d'un oubli mais une extension nouvelle, acceptée sur ses mérites propres (coût quasi nul, besoin plausible), pas sur la prémisse qu'elle aurait déjà été validée. Aucun système d'authentification ou de permissions n'est construit ici — uniquement le champ et sa valeur par défaut. 

- Documents impactés — Code source uniquement. Statut — Validé. 

### — ADR-021 Traduction du Data Model en schéma PostgreSQL (Étape 1 du pivot backend) 

- Décision — Le Data Model conceptuel (26 entités) est traduit en schéma relationnel avec 6 écarts 

- documentés : (1) relation Devis ↔ OrdreReparation rendue unidirectionnelle pour éviter un cycle de clés étrangères, (2) `KPIDefinition.filtre` (fonction JS) remplacé par un critère JSON déclaratif, (3) "semaine" (étiquette texte) remplacée par de vraies dates de période, (4) `HistoriqueStatut.entite_id` sans contrainte de clé étrangère réelle (référence polymorphe, limite connue de SQL), (5) spécialités techniciens normalisées en table de liaison, (6) identifiants texte remplacés par des UUID. 

- Contexte — Premier chantier du pivot vers une architecture backend réelle (Python/FastAPI, PostgreSQL/Supabase), motivé par l'objectif de faire d'APEX un produit utilisable par plusieurs clients réels plutôt qu'un prototype HTML autonome. 

- Justification — Chaque écart a été signalé plutôt que corrigé silencieusement, conformément à la demande explicite ; le schéma a été testé contre un vrai PostgreSQL (30 tables, 4 index créés sans erreur) et vérifié par un jeu de données incluant 3 tests négatifs délibérés (doublon, statut invalide, clé étrangère inexistante), tous correctement rejetés par les contraintes. 

- Documents impactés — `APEX_schema.sql` , 

- `APEX_Backend_Migration_Notes.md` . 

- Statut — Validé (schéma), écart n°4 (HistoriqueStatut) laissé comme risque connu et documenté plutôt que résolu. 

### — ADR-022 Précision de gouvernance sur l'ambition produit 

- Décision — Le pivot vers un backend réel est acté à partir de ce point, mais la présentation de ce pivot comme un simple "rappel de la vision" est corrigée : l'ambition d'un produit vendable à plusieurs clients réels (réseaux de la taille de Renault/Toyota/Fiat) n'avait jamais été formulée avant le message déclenchant ce pivot. Le cadrage initial du projet (première session) définissait explicitement une entreprise fictive à but méthodologique. 

- Contexte — Cohérence historique du journal de décisions : un ADR doit refléter ce qui a réellement été décidé et quand, pas une reconstruction rétroactive de l'historique du projet. 

- Justification — Cette précision n'invalide pas le pivot ni les décisions techniques qui en découlent — elle garantit seulement que le registre reste une source de vérité fiable sur la chronologie réelle des décisions, principe déjà appliqué à plusieurs reprises dans ce projet (cf. ADR-012, correction Étape 3). 

- Documents impactés — Aucun changement technique ; clarification du journal de décisions uniquement. 

- Statut — Validé. 

### — ADR-023 Couche Recommendation, extension distincte du KPI Engine 

- Décision — Une couche `Recommendation` , consommant les `KPIValue` déjà calculées, produira périodiquement des analyses comparatives (meilleur/pire technicien, produit, réparation) et des suggestions concrètes. Elle constitue une extension séparée du KPI Engine, jamais une modification de son cœur : le moteur continue de ne produire que des valeurs et des statuts, jamais de texte interprétatif (cf. Étape 4, point 5 — "ne jamais contenir de texte destiné à l'utilisateur final"). Deux approches de génération du texte sont documentées sans trancher : règles codées en dur (if/else) — maintenable, prévisible, mais rigide et coûteuse à étendre KPI par KPI — versus appel à un LLM — flexible et capable de nuance, mais coût récurrent, latence, et risque de sortie non déterministe à encadrer (contredirait le principe de déterminisme du KPI Engine si mal isolé). Le choix réel est différé à l'implémentation. 

- Contexte — Objectif produit : dépasser le simple seuil excellent/watch/moderate/critical pour proposer une analyse actionnable, une fois le backend et le KPI Engine réel opérationnels sur données ERP. 

- Justification — Respecte la frontière déjà actée entre calcul et interprétation (Étape 4) ; consomme la représentation déclarative JSON de 

- `KPIDefinition.source_critere` actée à l'Étape 1 

- (ADR-021), pas l'ancienne fonction `filtre` du prototype HTML, désormais obsolète pour ce usage. 

- Tension signalée avec l'existant — Le module "AI Advisor" (APEX v2.0) est conceptuellement la préfiguration de cette couche : il avait été identifié dans l'audit v2.0 comme "texte statique pré-rédigé, pas une vraie analyse", avec la recommandation de le rendre dynamique ou de le renommer honnêtement (priorité 🟠 de la roadmap post-audit). Recommandation : `Recommendation` devrait devenir la véritable 

- implémentation dont `AI Advisor` était un placeholder, plutôt que deux systèmes parallèles construits séparément — à trancher explicitement au moment de l'implémentation, pas ici. 

#### Documents impactés — 

`APEX_KPI_Engine_Architecture.md` (à compléter d'une section "Recommendation" lors d'une prochaine révision), aucun changement de code à ce stade. 

- Statut — Documenté, non implémenté. 

### — ADR-024 Deux catégories de données : internes (ERP client) et externes (marché), fraîcheur différenciée 

- Décision — APEX distingue désormais deux catégories de données aux cycles de vie différents : données internes (factures, OR, achats — issues de l'ERP de chaque client, fraîcheur quasi temps réel, isolation stricte par client) et données externes (marché, concurrents — fraîcheur mensuelle/trimestrielle, mutualisation possible entre clients d'un même secteur). 

- Contexte — Conséquence directe de l'ambition multiclients actée (ADR-022) : deux natures de données qui 

ne devraient pas être traitées par le même pipeline de collecte ni la même politique d'isolation. 

Justification — Éviter de concevoir une collecte unique à fréquence unique qui serait soit trop coûteuse pour les données externes (aucune valeur à les rafraîchir en temps réel), soit trop lente pour les données internes (inacceptable pour un ERP client). 

- Tension signalée avec l'existant — Le schéma livré à l'Étape 1 (ADR-021) isole les données par 

- `concession_id` , sans entité "Compte Client / 

- Organisation" au-dessus de `Concession` . Or l'ambition multi-clients (ADR-022) implique qu'un client payant d'APEX (ex. un réseau automobile) puisse posséder plusieurs concessions, elles-mêmes à isoler d'un autre client payant. Question ouverte, non tranchée ici : `Concession` doit-elle rester l'unité d'isolation, ou une 

- entité parente ("Organisation"/"Compte Client") doit-elle être introduite au-dessus ? Cette question devra être résolue avant la connexion du premier ERP réel, pas après. 

- Documents impactés — `APEX_Data_Model.md` (question ouverte à ajouter lors d'une prochaine révision), aucun changement de code à ce stade. 

- Statut — Documenté, non implémenté ; contient une question ouverte non résolue. 

### — ADR-025 Stratégie de synchronisation ERP : polling incrémental 

- Décision — La stratégie par défaut de synchronisation avec les ERP clients est le polling incrémental (interrogation toutes les 2 à 5 minutes, filtrée par date 

de modification), pas les webhooks. Les webhooks restent une optimisation ponctuelle possible, en complément, jamais en remplacement de la stratégie par défaut. 

- Contexte — Hétérogénéité des ERP clients cibles (SAP, Odoo, systèmes maison) ; le support de webhooks n'étant pas garanti partout, une stratégie uniforme est préférée à une stratégie optimale mais fragile. 

- Justification — Résilience (un poll manqué est rattrapé par le suivant) et indépendance vis-à-vis des capacités spécifiques de chaque ERP — cohérent avec ADR-013 (indépendance vis-à-vis des systèmes externes, couche d'adaptation dédiée). Hypothèse explicitement posée : suppose que l'ERP cible expose un filtre par date de modification ; à défaut, écart à documenter au moment de l'intégration réelle (couche ERPAdapter). 

- Tension signalée avec l'existant — Le rejet d'une architecture Event-Driven pour le KPI Engine (discussion technique post-Étape 4) reposait explicitement sur l'absence de "véritable producteur d'événements" à ce moment du projet. Le polling incrémental, une fois construit, constituera ce producteur d'événements réel (changements détectés toutes les 2-5 minutes). Ce n'est pas une raison de reconstruire le KPI Engine en Event-Driven maintenant — la fréquence de calcul hebdomadaire (ADR-016) reste valable tant que les KPI actuels n'exigent pas une fraîcheur plus fine — mais c'est le signal explicite qui devra rouvrir cette question le jour où l'écart entre données quasi temps réel et calcul hebdomadaire deviendra un vrai problème métier, pas une hypothèse. 

#### Documents impactés — 

- `APEX_KPI_Engine_Architecture.md` (à compléter lors 

- d'une prochaine révision), aucun changement de code à ce stade. 

Statut — Documenté, non implémenté. 

### — ADR-026 Introduction d'une entité Organisation, frontière d'isolation entre clients payants 

- Décision — Nouvelle hiérarchie à trois niveaux : `Organisation` (compte client payant d'APEX) → `Concession` (un ou plusieurs établissements de cette 

- organisation) → toutes les données existantes, rattachées à une concession comme aujourd'hui. `concessions` reçoit `organisation_id NOT NULL` 

- `REFERENCES organisations(id)` . Aucune autre table modifiée : l'isolation par organisation se déduit par jointure via `concessions.organisation_id` , jamais par duplication du champ. 

- Contexte — Referme la question laissée ouverte à ADR024 : le schéma de l'Étape 1 isolait par `concession_id` sans notion de client payant pouvant posséder plusieurs concessions. 

- Justification (sécurité) — La frontière d'isolation entre clients payants doit être une frontière de schéma (contrainte SQL réelle), pas une discipline de code répétée à chaque requête — un `WHERE concession_id = ...` oublié dans une seule route applicative suffirait à faire fuiter les données d'un client vers un autre si l'isolation reposait uniquement sur la rigueur du développeur. Mécanisme prévu pour la phase API/Auth à venir : Row-Level Security (RLS) PostgreSQL sur 

`organisation_id` , non implémenté à ce stade — seule la frontière structurelle (la colonne et sa contrainte) est posée maintenant. 

Dénormalisation envisagée puis écartée — Dupliquer `organisation_id` directement sur les tables filtrées par concession ( `ordres_reparation` , `kpi_values` ...) aurait évité une jointure à chaque requête isolée par client. Écarté : aucune donnée de charge réelle ne justifie ce coût de duplication à ce stade ; un index sur `concessions.organisation_id` rend la jointure peu coûteuse pour les volumes actuels. À reconsidérer uniquement si une mesure réelle de performance le justifie. 

- Vérification — Schéma recréé sur PostgreSQL local (31 tables, 0 erreur) ; jeu de test étendu avec une organisation ; 4 tests négatifs (dont le nouveau : 

- `concession` avec `organisation_id` inexistant) tous 

- correctement rejetés. 

- Documents impactés — `APEX_schema.sql` , `APEX_schema_test.sql` . 

- Statut — Validé. Referme la question ouverte d'ADR024. 

### — ADR-027 Portage du KPI Engine vers Python (Étape 2 du pivot backend) 

- Décision — La logique du KPI Engine (Extracteur, Calculateur, Évaluateur, Écrivain) est portée fidèlement en Python, connectée à PostgreSQL. Bibliothèque 

- retenue : SQLAlchemy Core avec réflexion automatique du schéma ( `MetaData.reflect` ), pas de psycopg2 brut ni d'ORM déclaratif. 

- Contexte — Premier portage réel de la logique JavaScript déjà éprouvée (KPI-1/KPI-2) vers le backend réel amorcé à l'Étape 1 (schéma PostgreSQL). 

- Justification du choix de bibliothèque — psycopg2 brut aurait exigé du SQL réécrit à la main pour chaque nouvelle collection, sans réutilisation. Un ORM déclaratif aurait dupliqué la définition du schéma déjà posée dans `APEX_schema.sql` — deux sources de vérité pour la même structure, l'erreur exacte déjà corrigée par le principe des 3 niveaux (ADR-012). La réflexion automatique lit la structure réelle de la base à l'exécution : `APEX_schema.sql` reste l'unique source de vérité. SQLAlchemy Core (sans l'ORM complet) est également le choix le plus naturel pour une réutilisation par la future API FastAPI. 

- Écart signalé n°1 — colonne de date de période non déclarée au schéma : `kpi_definitions` ne précise nulle part quelle colonne de date de la collection source sert au filtrage par période ( `rendezvous.date_demande` ? `ordres_reparation.date_ouverture` ?). Résolu provisoirement par une correspondance codée en dur dans `extracteur.py` , signalée explicitement plutôt que corrigée en modifiant le schéma sans validation . Recommandation pour une prochaine étape : ajouter `kpi_definitions.date_champ_periode` pour rendre 

- cette information déclarative. 

- Écart signalé n°2 — bug réel détecté et corrigé pendant le test : `evaluer_statut()` levait une `TypeError` ( `Decimal` / `float` non compatibles nativement en Python) lors du premier calcul réel — un cas que le prototype JavaScript ne pouvait pas révéler puisque JS 

ne distingue pas ces deux types numériques. Corrigé par une conversion explicite ( `float(target)` ) avant le calcul de pourcentage. Ce n'est pas un écart de logique métier (la règle de seuils reste strictement identique), mais un écart de fidélité technique entre les types numériques de PostgreSQL et de JavaScript, qui n'aurait pu être découvert que par un test réel contre une vraie base — exactement la raison pour laquelle ce portage exige des tests réels et pas une relecture. 

- Fidélité du portage — Vérifiée par un test réel contre PostgreSQL local : les 2 KPI pilotes calculés par le module Python produisent des valeurs strictement identiques à un contrôle SQL manuel indépendant ; le recalcul (ADR-015) préserve `cree_le` / `cree_par` , met à jour `recalcule_le` , et ne crée aucun doublon (vérifié en comptant les lignes `kpi_values` après un second appel). 

- Documents impactés — Nouveau module 

- `kpi_engine_py/` (code), aucune modification du 

- schéma. 

- Statut — Validé. L'écart n°1 reste un point ouvert pour une prochaine étape (ne modifie pas le schéma sans validation explicite). 

### — ADR-028 Tolérance aux limites de débit (rate limits) pour le futur ERPAdapter 

- Décision — L'ERPAdapter (à construire lors de la connexion au premier ERP réel) devra respecter une limite de débit configurable par client, pas une fréquence de polling fixe unique. Le rythme cible de 2 à 5 minutes (ADR-025) reste l'objectif par défaut, à 

ajuster à la baisse si l'ERP d'un client impose une limite plus stricte. 

- Contexte — Complément à ADR-025 (polling incrémental) : les ERP clients cibles (SAP, Odoo, systèmes maison) ont des limites de débit d'API hétérogènes, non prises en compte lors de la décision initiale. 

- Justification — Un paramètre par client plutôt qu'une constante globale évite qu'un ERP moins permissif ne soit systématiquement en erreur, ou qu'un ERP plus permissif soit sous-exploité par une fréquence unique trop prudente. 

- Documents impactés — Note de conception pour l'ERPAdapter (à construire au moment de ce chantier) ; aucune implémentation à ce stade. 

- Statut — Documenté, non implémenté. Referme la question implicite laissée par ADR-025 sur ce point précis. 

### — ADR-029 Recommendation remplace AI Advisor (ferme la question ouverte d'ADR-023) 

- Décision — La couche `Recommendation` (ADR-023) est actée comme la véritable implémentation dont `AI Advisor` (APEX v2.0) était le placeholder. Aucune coexistence des deux systèmes : `AI Advisor` sera retiré (ou marqué obsolète puis retiré) au moment où `Recommendation` sera implémentée — pas avant, son 

- implémentation restant hors périmètre actuel. 

- Contexte — ADR-023 avait signalé la ressemblance conceptuelle entre les deux sans trancher. Cette entrée 

ferme explicitement ce point. 

- Justification — Évite deux systèmes parallèles pour le même besoin (déjà identifié dans l'audit v2.0 comme un défaut d' `AI Advisor` : texte statique pré-rédigé, pas une vraie analyse). Trancher la direction maintenant évite toute ambiguïté au moment de l'implémentation réelle. 

- Documents impactés — ADR-023 (tension désormais résolue, voir cette entrée) ; aucune implémentation à ce stade. 

- Statut — Validé. Referme la question ouverte d'ADR-023 sur ce point précis. 

### — ADR-030 Confirmation : trigger de validation HistoriqueStatut reste différé 

- Décision — La décision actée à ADR-021 (signaler le risque d'intégrité sur `historique_statut.entite_id` plutôt que construire un trigger de validation applicative maintenant) est confirmée et maintenue telle quelle. 

- Contexte — Clôture explicite d'un point resté implicitement ouvert depuis ADR-021, sans nouvelle information justifiant un changement. 

- Justification — Aucune donnée réelle ne permet à ce stade de dimensionner correctement les règles d'un tel trigger ; le construire maintenant serait une anticipation non justifiée (principe de gouvernance n°3). 

- Documents impactés — Aucun. 

- Statut — Confirmé sans changement. 

### — ADR-031 Ajout de 

### kpi_definitions.date_champ_periode (ferme l'écart signalé à ADR-027) 

- Décision — `kpi_definitions` reçoit une colonne 

- `date_champ_periode TEXT NOT NULL` , renseignée pour 

- les 2 KPIDefinition pilotes ( `date_demande` pour `kpidelai-rdv` , `date_ouverture` pour `kpi-nombre-or` ). Le dictionnaire codé en dur 

- `COLONNE_DATE_PAR_COLLECTION` est retiré 

- d' `extracteur.py` , qui lit désormais cette information depuis la définition chargée en base. 

- Contexte — Referme explicitement l'écart signalé à ADR-027 : la colonne de date utilisée pour le filtrage par période n'était pas déclarative. 

- Justification — Rend l'information réutilisable par tout futur outil (API, interface d'administration des KPI) sans dépendre du code Python de l'Extracteur ; cohérent avec le principe déjà appliqué à `source_critere` (ADR021) : les définitions de KPI doivent rester intégralement déclaratives. 

- Vérification — Schéma reconstruit et testé de bout en bout (31 tables — cet ajout est une colonne sur `kpi_definitions` , pas une nouvelle table) ; les 2 KPI 

- pilotes recalculés produisent des valeurs strictement identiques à avant ce correctif (3,5 j / 4 RDV, 3 OR) — confirmé : changement de représentation, pas de comportement. 

- Documents impactés — `APEX_schema.sql` , `kpi_engine_py/extracteur.py` , 

- `APEX_schema_test.sql` , `APEX_enrichir_test.sql` . 

#### Statut — Validé. Referme ADR-027. 

### — ADR-032 API FastAPI exposant le KPI Engine 

### (Étape 3 du pivot backend) 

- Décision — API FastAPI minimale : `GET /health` , `GET /kpi-definitions` , `POST /kpi/{kpi_id}/calculer` , `GET /kpi/{kpi_id}/valeurs` , `GET /kpi-` 

- `values/{id}/sources` . Aucune logique métier dans la couche API : elle route et sérialise, `kpi_engine_py` (Étape 2) reste inchangé. 

- Contexte — Premier point d'accès HTTP réel au moteur KPI porté à l'Étape 2, condition pour une future connexion ERP et une future interface utilisateur réelle. 

- Décision d'architecture — gestion de connexion : engine SQLAlchemy et métadonnées réfléchies créés une seule fois au démarrage (lifespan FastAPI), pas à chaque requête (la réflexion du schéma coûterait un aller-retour réseau par appel) ; une connexion par requête via injection de dépendance ( `Depends` ), fermée automatiquement en fin de requête. 

- Écart signalé n°1 — fonction de provenance non portée à l'Étape 2 : l'équivalent Python de 

`kpiResoudreSourcesReelles` (JS) n'existait pas encore — le périmètre de l'Étape 2 se limitait au calcul, pas à la résolution de provenance. Ajouté maintenant ( `kpi_engine_py/provenance.py` ), signalé plutôt que silencieusement supposé déjà fait. 

- Écart signalé n°2 — bug réel détecté et corrigé pendant le test : `ResponseValidationError` sur 

- `id` / `concession_id` — PostgreSQL renvoie des objets `UUID` natifs via psycopg2/SQLAlchemy, les schémas 

Pydantic déclaraient `str` . Corrigé en déclarant ces champs en type `UUID` (Pydantic sérialise nativement vers une chaîne en JSON). Un cas qu'une relecture de code n'aurait pas nécessairement révélé — détecté uniquement par l'exécution réelle contre PostgreSQL. 

- Fidélité du portage confirmée à travers la couche API : le test réel confirme qu'ADR-015 (recalcul automatique, `cree_par` / `cree_le` préservés) tient bout en bout, de 

- l'appel HTTP jusqu'à l'écriture en base — `cree_par` reste celui du calcul d'origine (Étape 2) malgré un nouvel appel API avec un auteur différent. 

- Documents impactés — Nouveau dossier `api/` (code), nouveau module `kpi_engine_py/provenance.py` . 

- Statut — Validé. 

### — ADR-033 Confirmation du déploiement réel sur Supabase (première infrastructure hors bac à sable local) 

- Décision — Le schéma ( `schema.sql` ) et les jeux de données de test ( `test_data.sql` , 

- `enrichir_test.sql` ) sont déployés avec succès sur 

- une véritable instance Supabase PostgreSQL, exécutés directement par Abdeljalil via le SQL Editor Supabase — les trois scripts s'exécutent sans erreur, tables et données vérifiées visuellement dans le Table Editor. 

- Contexte — Mon bac à sable ne peut pas atteindre `supabase.co` ( `x-deny-reason: host_not_allowed` , 

- confirmé par diagnostic réseau) : cette étape a donc nécessité une exécution directe par Abdeljalil depuis son propre poste, pas par moi. Premier test réel de 

portabilité du schéma en dehors de l'environnement local où il avait été conçu et validé (Étape 1). 

Justification / vérification — Vérification effectuée par Abdeljalil directement (exécution SQL Editor + inspection Table Editor), pas par un test automatisé de ma part sur cet environnement précis — différence méthodologique à noter : c'est la première vérification de ce projet qui n'a pas été exécutée par moi. 

Mesure de sécurité appliquée — Le mot de passe partagé en clair dans la conversation a été changé immédiatement après usage, sur recommandation explicite donnée avant l'exécution ; l'ancien lien de connexion n'est plus valide. 

#### Ce qui n'est PAS encore confirmé — 

`test_engine_reel.py` et `test_api_reel.py` (le moteur KPI et l'API, pas seulement le schéma et les données) n'ont pas encore été exécutés contre Supabase. Le succès du chargement du schéma et des données ne garantit pas encore que le moteur Python et l'API fonctionnent correctement contre cette instance réelle (latence réseau différente, éventuelles différences de configuration Supabase vs PostgreSQL local) — à vérifier avant de considérer cette étape totalement close. 

- Documents impactés — Aucun changement de code ; confirmation d'infrastructure. 

- Statut — Partiellement validé : schéma et données confirmés en production réelle ; moteur KPI et API encore à vérifier contre cette même instance. 

### — ADR-034 Fermeture de la vérification ouverte à ADR-033 : moteur KPI et API confirmés contre Supabase réel 

- Décision — `test_engine_reel.py` et 

- `test_api_reel.py` exécutés avec succès contre 

- l'instance Supabase réelle (pas seulement le schéma et les données comme à ADR-033) : tous les tests passent, y compris le recalcul (ADR-015), les routes GET/POST de l'API, et les cas d'erreur 404. 

- Contexte — Ferme explicitement la limite signalée à ADR-033 ("ce qui n'est pas encore confirmé"). 

- Écart technique rencontré et résolu — Connexion directe via l'hôte Supabase par défaut incompatible (résolution IPv6 sans route IPv4 disponible depuis l'environnement d'Abdeljalil). Résolu en utilisant le point de connexion Session Pooler de Supabase (IPv4) à la place de l'hôte direct — changement d'URL de connexion uniquement, aucune modification de schéma, de code applicatif, ni de logique. Signalé ici plutôt que passé sous silence : quiconque reprendra ce projet devra utiliser le Session Pooler, pas l'hôte direct, dans un contexte réseau IPv4 uniquement. 

- Justification — Le moteur KPI (extraction, calcul, seuils, écriture, recalcul) et l'API qui l'expose fonctionnent identiquement en conditions réelles de production (latence réseau réelle, infrastructure Supabase) qu'en local — aucune divergence de comportement détectée. 

- Documents impactés — Aucun changement de code ni de schéma ; seule la chaîne de connexion utilisée par Abdeljalil diffère (Session Pooler), à documenter dans 

les instructions de déploiement pour éviter que ce point ne soit redécouvert plus tard. 

Statut — Validé. Ferme ADR-033. 

### — ADR-035 Table de liaison membres_organisation (rattachement utilisateur ↔ organisation) 

- Décision — Nouvelle table `membres_organisation` ( `user_id UUID` , `organisation_id UUID REFERENCES organisations(id)` , `role TEXT` , clé primaire composite). `user_id` référence l'identité gérée par Supabase Auth ( `auth.users` , schéma propre à Supabase) — pas de contrainte de clé étrangère crossschéma réelle (limite technique connue, similaire au choix déjà fait pour `historique_statut.entite_id` à ADR-021), l'intégrité de cette référence est assurée côté application (l'API ne fait confiance qu'à un `user_id` extrait d'un token JWT valide, jamais saisi librement). 

- Contexte — Étape 4 (authentification) exige de savoir à quelle(s) organisation(s) un utilisateur authentifié a accès, pour autoriser ou refuser une requête sur une `concession_id` donnée. 

- Justification — Complète la hiérarchie Organisation → Concession actée à ADR-026 : sans cette table, aucune autorisation réelle n'est possible entre l'identité d'un utilisateur (Supabase Auth) et les données qu'il a le droit de voir. 

- Documents impactés — `APEX_schema.sql` (nouvelle table), `api/auth.py` (vérification d'appartenance à l'organisation avant d'autoriser un calcul KPI sur une concession donnée). 

- Statut — Validé, à implémenter immédiatement dans cette même étape. 

### — ADR-036 Authentification JWT (Supabase Auth) et autorisation par organisation (Étape 4) 

- Décision — Les 5 routes de l'API exigent désormais un token Bearer valide (vérifié via `SUPABASE_JWT_SECRET` , algorithme HS256, audience `authenticated` ). Les routes portant sur une `concession_id` vérifient en plus que l'utilisateur est membre ( `membres_organisation` , ADR-035) de l'organisation propriétaire de cette concession — sinon 403. Le champ `auteur` fourni par le client est retiré du schéma de requête : `cree_par` provient exclusivement de l'identité extraite du token ( `sub` ), jamais d'une valeur fournie librement par l'appelant. 

- Contexte — Périmètre défini et validé pour l'Étape 4 : remplacer l'écran de connexion prototype (documenté comme non sécurisé depuis la v2.0) par une authentification réelle. 

- Justification — Empêche qu'un client authentifié puisse usurper l'identité d'un autre auteur en le fournissant simplement dans le corps de la requête ; l'autorisation par organisation applique concrètement la frontière d'isolation actée à ADR-026, jusqu'ici seulement structurelle (contrainte SQL) et pas encore appliquée au niveau applicatif. 

- Vérification réelle — Test complet (FastAPI TestClient + PostgreSQL local, JWT de test signé avec un secret local, jamais le vrai secret Supabase) : token absent/invalide → 401 ; token valide → 200 ; 

concession hors organisation de l'utilisateur → 403 ; recalcul d'une KPIValue pré-existante préserve 

`cree_par` d'origine (ADR-015 confirmé à travers la couche HTTP) ; première création d'une KPIValue 

attribue correctement `cree_par` à l'identité du token. 

- Écart rencontré pendant le test (non un bug) — Un token de test généré avec une expiration d'1 heure a expiré entre deux tours de la session (temps réel écoulé, pas un défaut du code) — le rejet par `jose` était le comportement correct. Noté ici comme rappel pratique pour la suite : toujours régénérer un token frais avant un nouveau test, en particulier avec de vrais tokens Supabase (expiration par défaut similaire, généralement 1 heure). 

- Documents impactés — `api/auth.py` (nouveau), `api/main.py` , `api/schemas.py` , `APEX_schema.sql` 

- (table `membres_organisation` , ADR-035), `.env.example` . 

- Statut — Validé en local. Reste à confirmer par Abdeljalil contre Supabase réel (vrai 

- `SUPABASE_JWT_SECRET` , vrai token émis par Supabase 

- Auth) avant clôture définitive de l'Étape 4. 

### — ADR-037 Vérification JWT via JWKS/ES256 

### (remplace le secret partagé HS256) 

- Décision — `auth.py` est réécrit pour vérifier les tokens via le point de publication des clés publiques Supabase (JWKS, `SUPABASE_URL/auth/v1/.well-` 

- `known/jwks.json` ), algorithme ES256, plutôt que via un secret partagé ( `SUPABASE_JWT_SECRET` , HS256). 

`SUPABASE_JWT_SECRET` est retiré de `.env.example` , remplacé par `SUPABASE_URL` . 

- Contexte — Le test réel contre le projet Supabase d'Abdeljalil (ADR-036) a révélé que le projet est intégralement migré vers les "JWT Signing Keys" asymétriques, sans option de retour à HS256 — confirmé directement depuis le Dashboard Supabase, pas une supposition. 

- Justification — Ce n'est pas seulement une contrainte imposée : c'est objectivement plus sûr. En HS256, vérifier un token exige de connaître le même secret que celui qui l'a signé — un secret qui fuit permet de forger n'importe quel token. En ES256/JWKS, seule la clé publique est distribuée ; la clé privée ne quitte jamais les serveurs Supabase. Aucun secret à protéger côté APEX pour la vérification. 

- Choix technique — Bibliothèque `PyJWT[crypto]` avec `PyJWKClient` (cache des clés en mémoire, pas d'appel 

- réseau à chaque requête — même principe que l'engine SQLAlchemy créé une fois au démarrage, ADR-032). Support ES256 uniquement, pas de repli HS256 : le projet cible ne l'accepte plus, ajouter un chemin mort serait une complexité non justifiée (principe de gouvernance n°3). 

- Vérification réelle — Un serveur JWKS local 

- ( `mock_jwks_server.py` ) génère une vraie paire de clés EC P-256 et signe un vrai token ES256 — teste le même mécanisme cryptographique exact que Supabase, sans dépendre d'un accès réseau à `supabase.co` (toujours bloqué depuis mon bac à sable, ADR-033). Tous les tests déjà validés à ADR-036 repassent à l'identique 

(401/403/200/404, `cree_par` correctement issu du token, ADR-015 confirmé). 

Documents impactés — `api/auth.py` (réécrit), 

- `.env.example` , nouveau `mock_jwks_server.py` (outil 

- de test uniquement, pas un composant de production). 

- Statut — Validé en local avec un mécanisme cryptographique équivalent. Reste à confirmer par Abdeljalil contre le vrai JWKS Supabase 

- ( `test_engine_reel.py` déjà validé contre Supabase réel à ADR-034 ; `test_api_reel.py` encore à exécuter contre Supabase réel avec cette version corrigée). 

### — ADR-038 Étape 4 confirmée intégralement contre Supabase réel (ferme ADR-036 et ADR-037) 

- Décision — L'authentification JWT (JWKS/ES256) et l'autorisation par organisation sont confirmées fonctionnelles contre l'infrastructure Supabase réelle d'Abdeljalil : base de données réelle (Session Pooler, ADR-034), vrai token émis par Supabase Auth, vrai endpoint JWKS — plus aucune composante simulée ou locale dans cette vérification. 

- Contexte — Ferme la dernière limite encore ouverte à ADR-037 ("reste à confirmer... test_api_reel.py contre le vrai JWKS Supabase"). 

- Vérification — Suite de tests complète exécutée par Abdeljalil directement contre Supabase : tous les cas passent (authentification, autorisation par organisation, recalcul ADR-015, provenance ADR-010, erreurs 404/403/401). 

- État du projet à ce stade — Chaîne complète validée en conditions réelles : Data Model (Étape 1) → moteur KPI Python (Étape 2) → API FastAPI (Étape 3) → authentification/autorisation (Étape 4), du schéma SQL jusqu'à un appel HTTP authentifié, sur infrastructure de production réelle (pas un environnement de simulation). 

- Documents impactés — Aucun changement de code. Confirmation finale. 

- Statut — Validé. Ferme ADR-036 et ADR-037. Étape 4 officiellement close. 

### — ADR-039 Correction d'état RLS + prototype frontend de validation de chaîne 

- Correction actée (pas une nouvelle décision) — RLS deny-by-default était déjà activé sur les 32 tables depuis plusieurs semaines, fait directement par Abdeljalil sur Supabase, indépendamment de moi. Je l'avais présenté à tort comme une action à venir dans mon message précédent. Corrigé ici : seules les policies fines (filtrage par `organisation_id` ) restent à faire, pas l'activation elle-même. 

- Décision 1 — script de vérification indépendante — `verifier_rls_anon.py` teste l'accès via la clé anon 

- Supabase (PostgREST), sans passer par le rôle `postgres` ni par notre API : preuve directe plutôt 

- qu'une déclaration. Un résultat "accès autorisé" y serait une régression de sécurité réelle, pas un simple écart — traité comme tel si constaté. 

- Décision 2 — priorisation : prototype frontend minimal avant policies RLS fines et avant ERP réel, décidé par Abdeljalil. Justification retenue : RLS fine n'est pas 

urgente tant que l'unique accès aux données passe par l'API FastAPI (rôle `postgres` , RLS contourné côté serveur applicatif) et que l'autorisation applicative (ADR-035/036) est déjà testée avec succès ; le vrai point bloquant pour la suite (ERP réel) est de valider visuellement la chaîne complète. 

- Livrable — `frontend_prototype/index.html` : page unique, séparée du prototype HTML existant (non modifié), flux réel (connexion Supabase Auth email/mot de passe → appel `POST /kpi/{id}/calculer` avec le token de session → affichage brut du résultat). CORS activé sur l'API ( `allow_origins=["*"]` ), explicitement documenté comme dette de sécurité assumée pour ce stade prototype , à restreindre avant toute mise en production réelle. 

- Vérification réelle effectuée — Chaîne API + CORS 

- testée via `TestClient` (requête POST avec en-tête `Origin` + requête `OPTIONS` de preflight, exactement 

- comme un vrai navigateur) : 200, en-tête `AccessControl-Allow-Origin` présent, preflight 200. Non testé depuis ce bac à sable (limite réseau déjà documentée, ADR-033) : le flux de connexion Supabase Auth réel dans un vrai navigateur — à confirmer par Abdeljalil, même méthode que toutes les étapes précédentes. 

#### Documents impactés — 

- `frontend_prototype/index.html` (nouveau), `api/main.py` (CORS), `verifier_rls_anon.py` 

- (nouveau), `test_prototype_chaine.py` (nouveau). 

- Statut — Correction d'état validée. Prototype validé pour la partie API/CORS ; connexion Supabase Auth réelle en 

attente de confirmation par Abdeljalil. 

### — ADR-040 Confirmation finale : RLS prouvé, prototype frontend validé de bout en bout (ferme ADR-039) 

- Décision — Les deux vérifications demandées à ADR039 sont closes avec preuve directe, pas une déclaration. 

- RLS (Demande 1) — `verifier_rls_anon.py` confirme un refus sur les 5 tables testées (HTTP 200 + 0 ligne), vérifié comme non dû à des tables vides (inspection manuelle du Table Editor : données bien présentes). Confirmé également par Supabase lui-même (tooltip Dashboard : RLS activé sans policy = refus total). Preuve indépendante, pas une supposition. 

- Prototype frontend (Demande 2) — Chaîne complète validée en conditions réelles : connexion Supabase Auth réelle (navigateur réel, compte `test@apex.local` ) → token réel → `POST /kpi/kpi-nombre-or/calculer` → HTTP 200 avec résultat correct ( `valeur: 3` , `nb_enregistrements_sources: 3` , cohérent avec les 

- vérifications précédentes). 

- Confirmation notable — `cree_par` est resté `"testetape2"` (l'auteur d'origine du calcul, Étape 2) malgré une connexion avec un utilisateur différent 

- ( `test@apex.local` ) à ce tour : preuve qu'ADR-015 (recalcul automatique, préservation de la paternité d'origine) fonctionne bout en bout à travers la chaîne complète réelle (navigateur → Supabase Auth → API → moteur → base), pas seulement en local ou via un test automatisé. 

- État du projet à ce stade — Auth réel → API réel → RLS confirmé → Frontend confirmé : les 4 maillons de la chaîne validés indépendamment et ensemble, sur infrastructure de production réelle. 

- Documents impactés — Aucun changement de code. Confirmation finale. 

- Statut — Validé. Ferme ADR-039. 

### — ADR-041 Report de RLS fine et de la restriction CORS, critère corrigé, mesure compensatoire documentée 

- Décision — RLS fine (policies par `organisation_id` ) et restriction CORS sont reportées, pas abandonnées, sous un critère unique et corrigé : "avant tout nouveau chemin d'accès externe utilisant directement une clé 

- `anon` / `authenticated` (application mobile, intégration 

- partenaire, tout accès contournant FastAPI)" — explicitement PAS "avant connexion ERP", puisque l'ERPAdapter écrira via un rôle de service fiable (même modèle que l'API actuelle avec le rôle `postgres` ), sans changer le modèle de menace que RLS fine adresserait. 

- Contexte — Le seul chemin d'accès externe direct aujourd'hui (clé `anon` ) est déjà bloqué intégralement par RLS deny-by-default (ADR-039/040, prouvé). L'autorisation applicative (ADR-035/036) protège déjà le seul chemin réellement utilisé (l'API). RLS fine protégerait contre un risque réel mais non encore exploitable (oubli humain d'une vérification 

- d'autorisation dans une future route) — un vrai risque de 

"defense in depth", pas un risque fictif, mais sans urgence tant qu'aucun nouveau chemin d'accès n'existe. 

- Mesure compensatoire actée, pas un oubli — Un test de régression statique 

( `test_regression_autorisation.py` ) vérifie que toute route de l'API référençant `concession_id` appelle bien `_exiger_acces_organisation` — protège contre l'oubli humain futur à un coût très inférieur à RLS fine, sans construire l'infrastructure RLS elle-même. 

Justification — Cohérent avec le principe déjà appliqué à plusieurs reprises (ADR-007, ADR-011) : pas de protection construite pour un risque sans chemin d'exploitation réel actuel, tant qu'une mesure compensatoire à faible coût couvre le risque résiduel identifié. 

#### Vérification réelle du test lui-même — 

`test_regression_autorisation.py` exécuté sur le code actuel : 3 routes conformes ( `calculer` , 

`lister_valeurs` , `sources_kpi_value` ). Preuve que le test détecte réellement une omission, pas seulement qu'il passe par construction : vérification supprimée artificiellement d'une route ( `lister_valeurs` ), le test échoue correctement ( ❌ détecté) ; code restauré, le test repasse au vert. Le test protège donc réellement contre l'oubli futur, pas seulement en théorie. 

Correctif de portabilité (relevé par Abdeljalil) — La première version codait en dur un chemin absolu propre à mon bac à sable 

( `/home/claude/apex_backend/api/main.py` ), inutilisable sur la machine d'Abdeljalil (Windows). Corrigé : chemin par défaut calculé relativement à 

l'emplacement du script 

( `Path(__file__).resolve().parent` ), plus une option `--main-path` pour le surcharger explicitement. Revérifié dans 3 configurations (depuis le dossier du script, depuis un dossier différent, avec `--main-path` explicite) — les trois fonctionnent identiquement. 

#### Documents impactés — 

`test_regression_autorisation.py` (nouveau). RLS fine et CORS restent documentés dans ADR-039 comme dette explicite, réactivée par ce nouveau critère. 

- Statut — Validé. Report assumé et documenté, pas silencieux. 

### — ADR-042 ERPAdapter AtlasCom initial (lecture + 

### transformation), lacune pieces.code_externe signalée 

- Décision — `erp_adapters/atlascom_adapter.py` lit `article.dbf` (encodage cp850) et transforme chaque 

- enregistrement vers un format proche de `pieces` , en appliquant les correspondances confirmées par Abdeljalil : `LIBELLE` → `designation` , 

- `SEUIL` → `seuil_reappro` , `QTESTOCK` → `stock` , 

`PRIX1` → `prix_catalogue` . Aucune écriture en base à ce stade — lecture et transformation uniquement, conformément au périmètre demandé. 

- Contexte — Premier ERPAdapter réel du projet, condition posée dès ADR-013/025/028 (couche d'adaptation dédiée, indépendance vis-à-vis des systèmes externes). 

#### Les 3 points de mapping, CLOS avec preuve sur données réelles (pas une supposition) : 

1. `QTESTOCK` → `stock` — confirmé par comparaison directe avec l'interface AtlasCom elle-même (article DC1220, stock=0 exact, rupture de stock réelle constatée dans les deux sources). 

2. `PRIX1` → `prix_catalogue` — confirmé sur 5 codes distincts (DC1220, DC2220, DC2211, MT1220, MT2220), quantité et prix corrects dans les deux sources à chaque fois. Point clé qui expliquait une valeur qui semblait initialement élevée (45 000 MAD) : `article.dbf` contient aussi de l' équipement d'atelier lourd (volucompteurs — les distributeurs de carburant eux-mêmes), pas uniquement des pièces détachées de faible valeur. Le prix était juste, l'hypothèse implicite sur la nature du catalogue était incomplète. 

3. `CODE` → `code_externe` — confirmé présent sur l'ensemble des codes vérifiés. 

Note ouverte, non résolue (documentée comme telle, pas tranchée par une hypothèse) — `article.dbf` mélange des pièces détachées consommables (Business Process, étape 7) et de l'équipement lourd (volucompteurs). Question laissée explicitement ouverte : la table `pieces` telle que conçue est-elle le bon endroit pour ce second type d'article, ou une distinction devient-elle nécessaire ? Différé à un échantillon de données plus large, quand le besoin réel se manifestera — pas une décision à prendre sur la base d'un seul enregistrement. 

- COFOURN (fournisseur) — transmis tel quel sous `fournisseur_code_externe` ; nécessitera une table de 

- correspondance vers `fournisseurs.id` (UUID) avant toute écriture réelle, non construite ici (aucune écriture prévue à ce stade). 

- Lacune de schéma identifiée (pas appliquée) — `pieces` ne porte aujourd'hui aucun identifiant externe 

- stable. Proposition, non appliquée à APEX_schema.sql sans validation explicite : ajouter `code_externe TEXT` (nullable) à `pieces` , générique (réutilisable pour tout futur ERP connecté, pas spécifique à AtlasCom). 

- Vérification réelle effectuée — Code validé par Abdeljalil de façon indépendante (ré-exécution de `creer_dbf_test.py` + `atlascom_adapter.py` , résultat 

- identique) puis contre les vraies données AtlasCom sur 5 codes distincts, avec vérification croisée directe dans l'interface AtlasCom elle-même — pas une simple relecture de mapping théorique. 

#### Documents impactés — 

`erp_adapters/atlascom_adapter.py` , 

`creer_dbf_test.py` . `APEX_schema.sql` non modifié — `code_externe` reste une proposition en attente de validation. 

- Statut — Validé et clos pour les 3 correspondances de champs testées. 2 points restent ouverts par choix explicite (proposition `code_externe` en attente de validation ; diversité des types d'articles différée à un échantillon plus large). 

### — ADR-043 pieces.code_externe et 

### fournisseurs_mapping_externe (ferme les 2 points 

### ouverts d'ADR-042) 

- Décision 1 — `pieces` reçoit `code_externe TEXT` (nullable), générique — pas spécifique à AtlasCom, réutilisable pour tout futur ERP connecté. Condition pour rapprocher un article ERP d'une ligne `pieces` de façon fiable entre deux synchronisations, sans dépendre de la désignation textuelle (fragile). 

- Décision 2 — Nouvelle table 

- `fournisseurs_mapping_externe` ( `code_externe` , `source_erp` , `concession_id` , `fournisseur_id` , 

- UNIQUE sur les 3 premiers) : correspondance entre le code fournisseur d'un ERP externe (ex. `COFOURN` d'AtlasCom) et `fournisseurs.id` (UUID interne). Structure uniquement, table volontairement vide : le rapprochement réel nécessite les données fournisseurs réelles d'AtlasCom, non disponibles à cette session — chantier séparé, non commencé ici, conformément au périmètre demandé. 

- Contexte — Ferme les 2 points explicitement laissés ouverts à ADR-042 (proposition `code_externe` non appliquée ; `COFOURN` transmis tel quel sans table de correspondance). 

- Observation constatée, pas corrigée — `fournisseurs` n'a pas de `concession_id` (table globale), alors que `fournisseurs_mapping_externe` est scopée par 

- concession : un même code externe peut désigner un fournisseur différent selon l'ERP/la concession source, tandis que le fournisseur APEX cible reste un enregistrement global partagé. Cohérent avec le 

schéma existant, pas une incohérence nouvelle introduite ici — simplement signalé pour que ce ne soit pas redécouvert par surprise plus tard. 

- Justification — `code_externe` générique (pas `code_atlascom` ) : le même besoin se représentera 

- pour tout ERP futur (Odoo, etc.), autant le nommer sans présumer d'un ERP unique dès maintenant. 

- Vérification réelle effectuée — Schéma reconstruit intégralement sur PostgreSQL local (pas une relecture) : 33 tables (32 + `fournisseurs_mapping_externe` ), 0 erreur. `\d pieces` confirme `code_externe` présent en `TEXT` , nullable. `\d fournisseurs_mapping_externe` 

- confirme la structure attendue. `SELECT count(*)` confirme 0 ligne, comme demandé. 

- Ce qui n'a pas été fait, par choix explicite — Aucune exploration de `bonlivra` / `boncom` , aucune écriture réelle dans `pieces` — chantiers séparés à venir, non commencés à cette session, conformément à la consigne reçue. 

- Documents impactés — `APEX_schema.sql` (2 modifications : colonne + nouvelle table). 

- Statut — Validé et vérifié réellement. Ferme ADR-042. 

Prochaine entrée : ADR-044, à la prochaine décision d'architecture actée. 

