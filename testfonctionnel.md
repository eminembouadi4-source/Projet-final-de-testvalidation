# Plan de Tests Fonctionnels (Selenium) – CoolDeal (SK_PROJTESTFINAL)

**Objectif :** Valider les parcours utilisateurs critiques de bout en bout (E2E) via l'automatisation Selenium.
**Source :** Basé sur les flux identifiés dans `analyse_de_projet.md`.

---

## 1. Parcours Visiteur (Non connecté)

### TF-01 : Navigation et Recherche
*   **Objectif :** Vérifier que le visiteur peut naviguer et trouver des produits.
*   **Scénario :**
    1.  Ouvrir la page d'accueil (`/`).
    2.  Vérifier la présence du slider et des sections (Coups de cœur).
    3.  Cliquer sur le menu "Resto" (ou autre catégorie).
    4.  Vérifier que la liste des deals s'affiche.
    5.  Cliquer sur un deal pour voir le détail.
    6.  Vérifier que le prix et la description sont visibles.

### TF-02 : Ajout au Panier (Anonyme)
*   **Objectif :** Valider le panier sans compte utilisateur.
*   **Scénario :**
    1.  Aller sur une fiche produit.
    2.  Cliquer sur "Ajouter au panier".
    3.  Vérifier la notification ou la mise à jour du compteur panier header.
    4.  Aller sur la page Panier (`/deals/cart`).
    5.  Vérifier que le produit est bien listé avec la bonne quantité.
    6.  Modifier la quantité (ex: +1).
    7.  Vérifier que le total se met à jour.

---

## 2. Parcours Client (Authentification)

### TF-03 : Inscription (Création de compte)
*   **Objectif :** Valider le formulaire d'inscription.
*   **Scénario :**
    1.  Aller sur la page d'inscription (`/customer/signup`).
    2.  Remplir le formulaire avec des données valides (Username, Email, Pass, Confirm).
    3.  Soumettre le formulaire.
    4.  Vérifier la redirection vers le Login ou le Dashboard.
    5.  Vérifier la création de l'utilisateur en base (via Admin ou connexion réussie).

### TF-04 : Connexion et Déconnexion
*   **Objectif :** Valider l'authentification.
*   **Scénario :**
    1.  Aller sur la page de login (`/customer/login`).
    2.  Saisir login/password valides.
    3.  Valider.
    4.  Vérifier la présence du nom d'utilisateur dans le header.
    5.  Cliquer sur "Déconnexion".
    6.  Vérifier le retour à l'état anonyme.

### TF-05 : Gestion de Profil
*   **Objectif :** Modifier les infos personnelles.
*   **Scénario :**
    1.  Se connecter.
    2.  Accéder au profil (`/client/`).
    3.  Modifier le numéro de téléphone ou l'adresse.
    4.  Sauvegarder.
    5.  Vérifier que les modifications sont prises en compte (message succès / réaffichage).

---

## 3. Parcours Achat (Checkout)

### TF-06 : Tunnel de commande complet
*   **Objectif :** Valider tout le flux d'achat.
*   **Scénario :**
    1.  Se connecter.
    2.  Ajouter un produit au panier.
    3.  Aller au Panier.
    4.  Cliquer sur "Commander" (`Checkout`).
    5.  Remplir les informations de facturation (si non pré-remplies).
    6.  Valider la commande.
    7.  Vérifier la redirection vers le paiement (CinetPay - mock ou vérif URL).
    8.  Vérifier que la commande est créée dans l'historique (`/client/commande`).

---

## 4. Parcours Contact & Robustesse

### TF-07 : Formulaire de Contact
*   **Objectif :** Vérifier l'envoi de message.
*   **Scénario :**
    1.  Aller sur `/contact/`.
    2.  Remplir Nom, Email, Sujet, Message.
    3.  Envoyer.
    4.  Vérifier le message de confirmation (ou l'alerte JS).

### TF-08 : Gestion des Erreurs (Robustesse)
*   **Objectif :** Vérifier que le site ne crash pas sur des saisies invalides.
*   **Scénario :**
    1.  Login : Tenter une connexion avec mauvais mot de passe -> Vérifier message d'erreur.
    2.  Inscription : Tenter un email déjà utilisé -> Vérifier message d'erreur.
    3.  Panier : Tenter de mettre une quantité négative -> Vérifier comportement (blocage ou remise à 1).
    4.  Page 404 : Tenter une URL inexistante (`/xyz`) -> Vérifier l'affichage de la page 404 personnalisée.

---

## 5. Environnement de Test
*   **Navigateur :** Chrome (Headless ou GUI pour debug).
*   **Driver :** Selenium WebDriver (Python).
*   **Données :** Base de données de test (isolée de la prod) pré-peuplée avec :
    *   1 Admin
    *   1 Etablissement + Produits
    *   1 Client de test
    *   Configuration SiteInfo complète (pour éviter les crashs identifiés).
