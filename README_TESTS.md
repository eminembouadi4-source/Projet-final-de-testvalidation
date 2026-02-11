# Documentation des Tests - Projet CoolDeal

Ce fichier décrit les étapes nécessaires pour exécuter les différents types de tests mis en place sur le projet Django.

## 1. Prérequis
- Python 3.x installé
- Pip installé
- Environnement virtuel recommandé (virtualenv)
- Dépendances installées :
  ```bash
  pip install -r requirements.txt
  ```

## 2. Tests Unitaires
Ces tests vérifient le bon fonctionnement des modules individuels (views, models, context processors) de manière isolée.

*   **Commande :**
    ```bash
    python manage.py test website.tests customer.tests shop.tests client.tests
    ```
*   **Contenu :** Environ 125 scénarios (hors paiement tiers).
*   **Documentation de référence :** `Unitaire.md`

## 3. Tests d'Intégration
Ces tests valident les interactions entre différents composants et le parcours utilisateur.

*   **Commande :**
    ```bash
    # Exécuter un module de test spécifique (exemple)
    python manage.py test website.tests_integration_full
    ```
    *(Note : Remplacez `website.tests_integration_full` par le chemin vers vos fichiers de tests d'intégration spécifiques si différents).*
*   **Documentation de référence :** `analyse_test_integration.md`

## 4. Tests Fonctionnels (Selenium)
Ces tests automatisent un navigateur pour valider les flux critiques du point de vue de l'utilisateur final.

*   **Prérequis :** Navigateur Chrome/Chromium et `chromedriver` compatible installés.
*   **Commande :**
    ```bash
    # Si les tests fonctionnels sont dans un fichier spécifique, exemple :
    python functional_tests.py
    # OU via le runner Django si intégrés :
    python manage.py test functional_tests
    ```
*   **Documentation de référence :** `testfonctionnel.md` + Tests manuels décrits dans ce fichier pour les interactions complexes (Vue.js).

## 5. Analyse Statique
Vérification automatisée de la qualité du code (PEP8, sécurité, templates, bonnes pratiques).

*   **Commande :**
    ```bash
    python run_static_checks.py
    ```
*   **Documentation de référence :** `static.md`
*   **Résultat :** Génère `rprtstatictest.txt`

## 6. Génération du Rapport Global
Pour consolider tous les résultats dans un fichier Word professionnel (`Rapport_testfinal.docx`).

*   **Commande :**
    ```bash
    python generate_report.py
    ```
*   **Résultat :** `Rapport_testfinal.docx` (consolide unitaires, intégration, fonctionnels, statique).

---
**Auteur :** Équipe Projet CoolDeal
**Date de mise à jour :** 11 Février 2026
