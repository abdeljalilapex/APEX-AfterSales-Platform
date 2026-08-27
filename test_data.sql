-- Test d'intégrité : insertion d'un jeu de données minimal mais complet,
-- couvrant les relations les plus sensibles (Organisation/Concession,
-- Devis/OR, KPIDefinition/KPIValue, historique_statut polymorphe,
-- contraintes CHECK).

INSERT INTO organisations (id, nom, statut)
VALUES ('00000000-0000-0000-0000-000000000001', 'AutoPerf Group SA', 'actif');

INSERT INTO concessions (id, organisation_id, nom, marques, capacite_atelier)
VALUES ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', 'AutoPerf Group', ARRAY['Peugeot','Fiat','Jeep','Opel'], 10);

INSERT INTO clients (id, nom, concession_id, statut, preference_contact)
VALUES ('22222222-2222-2222-2222-222222222222', 'Karim Benali', '11111111-1111-1111-1111-111111111111', 'actif', 'SMS');

INSERT INTO vehicules (id, client_id, concession_id, marque, modele, motorisation, kilometrage)
VALUES ('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Peugeot', '308', 'thermique', 45000);

INSERT INTO postes (id, type, concession_id)
VALUES ('44444444-4444-4444-4444-444444444444', 'Entretien courant', '11111111-1111-1111-1111-111111111111');

INSERT INTO techniciens (id, nom, poste_habituel_id, concession_id)
VALUES ('55555555-5555-5555-5555-555555555555', 'Technicien A', '44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111');

INSERT INTO conseillers_service (id, nom, concession_id)
VALUES ('66666666-6666-6666-6666-666666666666', 'Conseiller Service 1', '11111111-1111-1111-1111-111111111111');

INSERT INTO rendezvous (id, client_id, vehicule_id, concession_id, date_demande, delai_obtention_jours, canal, statut)
VALUES ('77777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', now(), 3.5, 'Digital', 'honore');

INSERT INTO devis (id, concession_id, conseiller_service_id, montant, statut)
VALUES ('88888888-8888-8888-8888-888888888888', '11111111-1111-1111-1111-111111111111', '66666666-6666-6666-6666-666666666666', 180.00, 'valide');

INSERT INTO ordres_reparation (id, rendezvous_id, devis_id, client_id, vehicule_id, technicien_id, conseiller_service_id, poste_id, concession_id, statut)
VALUES ('99999999-9999-9999-9999-999999999999', '77777777-7777-7777-7777-777777777777', '88888888-8888-8888-8888-888888888888', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666', '44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'clos');

INSERT INTO controles_qualite (ordre_reparation_id, statut)
VALUES ('99999999-9999-9999-9999-999999999999', 'conforme');

-- Test historique_statut polymorphe
INSERT INTO historique_statut (entite_type, entite_id, statut_precedent, nouveau_statut)
VALUES ('ordre_reparation', '99999999-9999-9999-9999-999999999999', 'en_cours', 'clos');

-- Membre de l'organisation (Étape 4) : associe un user_id fictif (simule
-- un utilisateur Supabase Auth) à l'organisation de test, condition pour
-- que les tests d'autorisation (ADR-035) passent.
INSERT INTO membres_organisation (user_id, organisation_id, role)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'admin');

-- Test KPIDefinition / KPIValue avec critère JSON (remplace la fonction filtre)
INSERT INTO kpi_definitions (id, version, nom, unite, target, lower_better, source_collection, source_critere, date_champ_periode, agregation_type, agregation_champ)
VALUES ('kpi-delai-rdv', 1, 'Délai moyen de prise de RDV', 'j', 2, true, 'rendezvous', '{"champ":"statut","operateur":"=","valeur":"honore"}', 'date_demande', 'moyenne', 'delai_obtention_jours');

INSERT INTO kpi_values (kpi_id, version, periode_debut, periode_fin, concession_id, valeur, statut, sources_ids, nb_enregistrements_sources, cree_par)
VALUES ('kpi-delai-rdv', 1, '2026-07-20', '2026-07-26', '11111111-1111-1111-1111-111111111111', 3.5, 'critical', ARRAY['77777777-7777-7777-7777-777777777777'::uuid], 1, 'scheduler');

-- ---- Tests négatifs : ces requêtes DOIVENT échouer (contraintes actives) ----
-- Rejeu du calcul (même kpi/version/période/concession) -> doit violer la contrainte UNIQUE
DO $$
BEGIN
    BEGIN
        INSERT INTO kpi_values (kpi_id, version, periode_debut, periode_fin, concession_id, valeur, sources_ids, nb_enregistrements_sources)
        VALUES ('kpi-delai-rdv', 1, '2026-07-20', '2026-07-26', '11111111-1111-1111-1111-111111111111', 9.9, '{}', 0);
        RAISE EXCEPTION 'ERREUR DE TEST : le doublon aurait dû être rejeté par la contrainte UNIQUE';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'OK : contrainte UNIQUE kpi_values respectée (doublon rejeté)';
    END;

    BEGIN
        INSERT INTO ordres_reparation (client_id, devis_id, vehicule_id, technicien_id, conseiller_service_id, poste_id, concession_id, statut)
        VALUES ('22222222-2222-2222-2222-222222222222', '88888888-8888-8888-8888-888888888888', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666', '44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'statut_invalide');
        RAISE EXCEPTION 'ERREUR DE TEST : le statut invalide aurait dû être rejeté par CHECK';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK : contrainte CHECK sur ordres_reparation.statut respectée';
    END;

    BEGIN
        INSERT INTO vehicules (client_id, concession_id, marque, modele, motorisation)
        VALUES ('00000000-0000-0000-0000-000000000000', '11111111-1111-1111-1111-111111111111', 'Peugeot', '208', 'thermique');
        RAISE EXCEPTION 'ERREUR DE TEST : la FK client_id inexistante aurait dû être rejetée';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'OK : contrainte de clé étrangère vehicules.client_id respectée';
    END;

    BEGIN
        INSERT INTO concessions (organisation_id, nom)
        VALUES ('99999999-9999-9999-9999-999999999999', 'Concession orpheline (organisation inexistante)');
        RAISE EXCEPTION 'ERREUR DE TEST : organisation_id inexistant aurait dû être rejeté';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'OK : contrainte de clé étrangère concessions.organisation_id respectée (ADR-026)';
    END;
END $$;

SELECT 'Tables peuplées avec succès, contraintes actives vérifiées.' AS resultat;
