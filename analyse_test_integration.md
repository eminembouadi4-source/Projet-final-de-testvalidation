# Analyse des tests d'intégration - Projet CoolDeal (SK_PROJTESTFINAL)

**Date :** 1er février 2026  
**Référence :** Basé sur `analyse_de_projet.md`  
**Objectif :** Recenser les tests d'intégration à implémenter pour valider le bon fonctionnement des parcours utilisateurs et des interactions entre les applications.

---

## 1. Introduction

Les tests d'intégration vérifient que plusieurs composants (vues, templates, modèles, context processors, middleware) fonctionnent correctement ensemble. Ce document recense les tests à réaliser en s'appuyant sur l'architecture du projet et les points critiques identifiés dans l'analyse ergonomique.

### Périmètre
- Applications : **website**, **shop**, **customer**, **client**, **contact**
- Technologies : Django, Vue.js (formulaires), AJAX (Axios), Bootstrap
- Base de données : SQLite (dev), modèles partagés entre apps

---

## 2. Tests d'intégration par application

### 2.1 Application Website

#### 2.1.1 Page d'accueil (`/`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| W-01 | Affichage page accueil avec données complètes | SiteInfo, Banniere, About, Produit, Partenaire, Appreciation en base | GET `/` | 200, template index.html, toutes les sections rendues | Haute |
| W-02 | Affichage page accueil sans SiteInfo | Base vide (ou SiteInfo absent) | GET `/` | Erreur ou page partielle (risque identifié dans analyse) | Haute |
| W-03 | Affichage page accueil avec cart vide/anonyme | Session nouvelle, pas de panier | GET `/` | 200, pas d'erreur sur `cart.produit_panier.count` | Haute |
| W-04 | Intégration context processors | Base avec données minimales | GET `/` | cat, infos, cart, galeries, horaires présents dans le contexte | Haute |
| W-05 | Liens navigation header | Utilisateur anonyme | GET `/` | Liens Accueil, Deal, A Propos, Contact, Connexion valides | Moyenne |
| W-06 | Menu catégories déroulant | CategorieEtablissement en base | GET `/` | Catégories affichées avec liens vers `/deals/<slug>` | Moyenne |
| W-07 | Section "Coups de coeur" | Produits avec super_deal=True | GET `/` | Produits affichés avec prix, liens vers fiche produit | Moyenne |
| W-08 | Slider bannières | Banniere avec images | GET `/` | Images chargées, pas d'erreur si couverture null | Moyenne |
| W-09 | Partenaires avec image null | Partenaire sans image | GET `/` | Pas d'erreur (risque identifié) | Haute |

#### 2.1.2 Page À propos (`/a-propos`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| W-10 | Affichage page À propos | About, WhyChooseUs, SiteInfo | GET `/a-propos` | 200, sections About et Pourquoi nous choisir | Haute |
| W-11 | Page À propos sans About | Pas d'About en base | GET `/a-propos` | 200 ou gestion propre des listes vides | Moyenne |
| W-12 | Image About null | About avec image null | GET `/a-propos` | Pas d'erreur sur `.url` (risque identifié) | Haute |
| W-13 | Intégration infos.text_pourquoi_nous_choisir | SiteInfo présent | GET `/a-propos` | Texte affiché sans erreur | Moyenne |

#### 2.1.3 Page 404

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| W-14 | Affichage 404 | Aucune | GET `/page-inexistante-xyz` | 404, template 404.html, lien retour accueil fonctionnel | Haute |
| W-15 | Lien "Go to home" sur 404 | Aucune | GET `/page-inexistante`, clic lien | Redirection vers `/` (vérifier `href="{% url 'index' %}"`) | Moyenne |

---

### 2.2 Application Shop

#### 2.2.1 Liste des deals (`/deals/`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| S-01 | Liste produits | Produits en base | GET `/deals/` | 200, produits affichés en grille/liste | Haute |
| S-02 | Liste vide | Aucun produit | GET `/deals/` | 200, message ou liste vide | Moyenne |
| S-03 | Breadcrumbs | Aucune | GET `/deals/` | Accueil // Deals affiché | Moyenne |
| S-04 | Filtre par catégorie | CategorieEtablissement + produits | GET `/deals/<slug-categorie>` | Produits filtrés par catégorie | Haute |
| S-05 | Catégorie inexistante | Aucune | GET `/deals/slug-inexistant` | Redirection vers shop ou 404 | Haute |
| S-06 | Produits avec promotion | Produits avec date_debut_promo, date_fin_promo | GET `/deals/` | Prix barré + prix promo affichés | Moyenne |
| S-07 | Images produits | Produits avec/sans image | GET `/deals/` | Pas d'erreur si image manquante | Moyenne |

#### 2.2.2 Fiche produit (`/deals/produit/<slug>`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| S-08 | Affichage fiche produit | Produit existant | GET `/deals/produit/<slug>` | 200, détails produit, bouton "Ajouter au panier" | Haute |
| S-09 | Produit inexistant | Aucune | GET `/deals/produit/slug-inexistant` | 404 | Haute |
| S-10 | Bouton favoris (utilisateur connecté) | User + Customer, produit | GET fiche, clic favoris | Toggle favori, redirection, message | Moyenne |
| S-11 | Bouton favoris (anonyme) | Utilisateur non connecté | Clic favoris | Redirection login, message | Moyenne |
| S-12 | Ajout au panier (Vue.js + API) | Panier existant, produit | POST `/customer/cart/add/product` (JSON) | 200 JSON, produit ajouté | Haute |
| S-13 | Produits similaires | Produits même catégorie | GET fiche produit | 3 produits liés affichés | Moyenne |
| S-14 | Images produit (image, image_2, image_3) | Produit avec 3 images | GET fiche | Galerie zoom fonctionnelle | Basse |

#### 2.2.3 Panier (`/deals/cart`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| S-15 | Panier vide | Session sans panier ou panier vide | GET `/deals/cart` | 200, message panier vide ou contenu vide | Haute |
| S-16 | Panier avec produits | Panier + ProduitPanier | GET `/deals/cart` | Liste produits, quantités, totaux | Haute |
| S-17 | Suppression produit (API) | Panier avec produits | POST `/customer/cart/delete/product` | Produit retiré, JSON success | Haute |
| S-18 | Application coupon | Panier, CodePromotionnel valide | POST `/customer/cart/add/coupon` | Réduction appliquée, total mis à jour | Haute |
| S-19 | Coupon invalide | Panier | POST avec code inexistant | Message erreur, pas de modification | Moyenne |
| S-20 | Mise à jour quantité (API) | Panier avec produit | POST `/customer/cart/udpate/product` (typo URL) | Quantité mise à jour ou 404 si URL incorrecte | Haute |
| S-21 | Bouton checkout | Panier non vide | Clic "Proceder au paiement" | Redirection vers checkout ou login si anonyme | Haute |
| S-22 | Panier avec cart = "" (context processor) | Session problématique | GET `/deals/cart` | Pas d'erreur AttributeError (risque identifié) | Haute |

#### 2.2.4 Checkout (`/deals/checkout`)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| S-23 | Checkout anonyme | Utilisateur non connecté | GET `/deals/checkout` | Redirection vers login | Haute |
| S-24 | Checkout connecté | User + Customer + panier | GET `/deals/checkout` | 200, formulaire/étape paiement | Haute |
| S-25 | Intégration CinetPay | Config CinetPay (si dispo) | Processus paiement | Création Commande, redirection | Moyenne |
| S-26 | Callback paiement success | Commande créée | GET/POST `/deals/paiement/success` | Page confirmation, commande visible | Moyenne |

#### 2.2.5 Dashboard établissement (protégé)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| S-27 | Dashboard anonyme | Non connecté | GET `/deals/dashboard/` | Redirection login | Moyenne |
| S-28 | Dashboard client | User Customer (pas Etablissement) | GET `/deals/dashboard/` | 403 ou redirection | Moyenne |
| S-29 | Dashboard établissement | User Etablissement | GET `/deals/dashboard/` | 200, interface dashboard | Moyenne |

---

### 2.3 Application Customer

#### 2.3.1 Authentification

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| C-01 | Page login | Anonyme | GET `/customer/` | 200, formulaire login | Haute |
| C-02 | Login déjà connecté | User connecté | GET `/customer/` | Redirection index | Haute |
| C-03 | Login succès (username) | User existant | POST `/customer/post` (JSON username/password) | 200 JSON success, session créée | Haute |
| C-04 | Login succès (email) | User avec email | POST avec email comme identifiant | Authentification réussie | Moyenne |
| C-05 | Login échec | Mauvais identifiants | POST login | 200 JSON success: false, message erreur | Haute |
| C-06 | Login CSRF | Aucune | POST sans token CSRF | 403 ou gestion CSRF | Moyenne |
| C-07 | Déconnexion | User connecté | GET `/customer/deconnexion` | Session détruite, redirection login | Haute |

#### 2.3.2 Inscription

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| C-08 | Page inscription | Anonyme | GET `/customer/signup` ou `/customer/inscription` | Formulaire affiché | Haute |
| C-09 | Inscription succès | Données valides | POST inscription (nom, email, username, etc.) | User + Customer créés, redirect ou message | Haute |
| C-10 | Inscription email invalide | Email mal formé | POST | Message erreur, pas de création | Moyenne |
| C-11 | Inscription username/email doublon | User existant | POST | Message "utilisateur existe déjà" | Haute |
| C-12 | Inscription mot de passe ≠ confirmation | password != passwordconf | POST | Message "mot de passe incorrect" | Haute |
| C-13 | Inscription avec ville (City) | City en base | POST avec ville_id | Customer.ville renseigné | Moyenne |

#### 2.3.3 Mot de passe oublié

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| C-14 | Page mot de passe oublié | Anonyme | GET `/customer/forgot_password` | Formulaire email | Moyenne |
| C-15 | Demande reset email existant | User avec email | POST email | Token créé, email envoyé (ou mock) | Moyenne |
| C-16 | Demande reset email inexistant | Email inconnu | POST | Message ou même comportement (sécurité) | Moyenne |
| C-17 | Reset via lien token | Token valide | GET `/customer/reset-password/<token>/` | Formulaire nouveau mot de passe | Moyenne |
| C-18 | Reset token expiré | Token > 1h | GET reset | Message erreur ou redirection | Moyenne |

#### 2.3.4 APIs Panier (JSON)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| C-19 | add_to_cart - succès | Panier + Produit | POST panier, produit, quantite | JSON success, ProduitPanier créé/mis à jour | Haute |
| C-20 | add_to_cart - panier invalide | Panier id inexistant | POST | Erreur 500 ou JSON error | Haute |
| C-21 | add_to_cart - produit invalide | Produit id inexistant | POST | Erreur | Haute |
| C-22 | delete_from_cart - succès | ProduitPanier existant | POST panier, produit_panier | Produit retiré, JSON success | Haute |
| C-23 | update_cart - succès | ProduitPanier existant | POST panier, produit, quantite | Quantité mise à jour | Haute |
| C-24 | update_cart - URL typo | Vérifier `cart/udpate/product` | POST `/customer/cart/udpate/product` | Route existe (ou 404 si corrigé en update) | Haute |
| C-25 | add_coupon - code valide | CodePromotionnel actif | POST panier, coupon | Panier.coupon assigné | Moyenne |
| C-26 | add_coupon - code invalide | Code inexistant | POST | JSON success: false, message | Moyenne |

---

### 2.4 Application Client

#### 2.4.1 Espace client (profil, commandes)

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| CL-01 | Profil anonyme | Non connecté | GET `/client/` | Redirection login | Haute |
| CL-02 | Profil avec User Etablissement | User Etablissement (pas Customer) | GET `/client/` | Redirection index (try/except customer) | Haute |
| CL-03 | Profil client | User + Customer | GET `/client/` | 200, infos profil, dernières commandes | Haute |
| CL-04 | Liste commandes | Customer avec commandes | GET `/client/commande` | Commandes affichées, pagination | Haute |
| CL-05 | Liste commandes vide | Customer sans commande | GET `/client/commande` | 200, liste vide | Moyenne |
| CL-06 | Recherche commandes | Commandes existantes | GET `/client/commande?q=xxx` | Résultats filtrés | Moyenne |
| CL-07 | Détail commande | Commande existante | GET `/client/commande-detail/<id>/` | Détails + produits | Haute |
| CL-08 | Détail commande autre client | Commande d'un autre Customer | GET avec id autre | 404 | Haute |
| CL-09 | Liste souhaits (favoris) | User avec favoris | GET `/client/liste-souhait` | Produits favoris affichés | Moyenne |
| CL-10 | Paramètres | Customer | GET `/client/parametre` | Formulaire paramètres | Moyenne |
| CL-11 | Reçu PDF | Commande existante | GET `/client/receipt/<order_id>/` | PDF généré ou erreur gérée | Moyenne |

---

### 2.5 Application Contact

| ID | Test | Préconditions | Actions | Résultats attendus | Priorité |
|----|------|---------------|---------|--------------------|----------|
| CO-01 | Page contact | SiteInfo en base | GET `/contact/` | 200, formulaire, carte (map_url) | Haute |
| CO-02 | Page contact sans SiteInfo | Pas de SiteInfo | GET `/contact/` | 200 ou gestion infos null (risque) | Haute |
| CO-03 | Envoi formulaire contact (API) | Données valides | POST `/contact/contact/post` (JSON) | Contact créé, JSON success | Haute |
| CO-04 | Formulaire contact - email invalide | Email mal formé | POST | JSON success: false, message | Moyenne |
| CO-05 | Formulaire contact - champs vides | Champs manquants | POST | Message "renseigner correctement" | Moyenne |
| CO-06 | Newsletter | Email valide | POST `/contact/newsletter/post` | NewsLetter créé, JSON success | Moyenne |
| CO-07 | Newsletter email invalide | Email invalide | POST | JSON success: false | Basse |

---

## 3. Tests d'intégration transversaux

### 3.1 Context Processors

| ID | Test | Description | Priorité |
|----|------|-------------|----------|
| T-01 | Context processor `site_infos` avec SiteInfo | Toutes les pages ont `infos` si en base | Haute |
| T-02 | Context processor `site_infos` sans SiteInfo | `infos` = None, templates ne plantent pas | Haute |
| T-03 | Context processor `cart` - session nouvelle | `cart` cohérent (objet ou None, jamais "") | Haute |
| T-04 | Context processor `cart` - utilisateur connecté avec panier | Panier lié à customer + session | Haute |
| T-05 | Context processor `categories` | `cat` disponible pour menu déroulant | Moyenne |
| T-06 | Context processor `galeries` | `galeries` pour footer | Moyenne |
| T-07 | Context processor `horaires` | `horaires` pour footer | Moyenne |
| T-08 | Context processor `cities` | `cities` pour formulaires (inscription, etc.) | Moyenne |

### 3.2 Parcours utilisateur end-to-end

| ID | Parcours | Étapes | Priorité |
|----|----------|--------|----------|
| T-09 | Visiteur → Accueil → Deal → Fiche produit | GET /, clic Deal, clic produit | Haute |
| T-10 | Visiteur → Ajout panier (anonyme) | Panier créé via session, produit ajouté via API | Haute |
| T-11 | Visiteur → Inscription → Profil | Inscription, redirection, accès /client/ | Haute |
| T-12 | Visiteur → Login → Checkout | Login, panier, checkout | Haute |
| T-13 | Client → Favoris | Connexion, ajout favori, liste souhaits | Moyenne |
| T-14 | Client → Commande → Détail → PDF | Passage commande, détail, téléchargement reçu | Moyenne |
| T-15 | Etablissement → Dashboard → Articles | Login Etablissement, accès dashboard | Moyenne |
| T-16 | Contact → Envoi message | Remplissage formulaire, POST, message succès | Haute |

### 3.3 Sécurité et middleware

| ID | Test | Description | Priorité |
|----|------|-------------|----------|
| T-17 | CSRF sur formulaires POST | Requêtes sans token rejetées | Moyenne |
| T-18 | @login_required | Pages protégées redirigent si anonyme | Haute |
| T-19 | Accès admin | GET `/admin/` redirige vers login admin | Moyenne |
| T-20 | Fichiers statiques | GET `/static/...` retourne 200 | Basse |
| T-21 | Fichiers media | GET `/media/...` retourne 200 pour fichiers existants | Moyenne |

### 3.4 Gestion des erreurs (analyse_de_projet)

| ID | Test | Risque identifié | Priorité |
|----|------|------------------|----------|
| T-22 | Base vide - SiteInfo | Pas de crash sur infos.icon, infos.logo | Haute |
| T-23 | Base vide - Panier | Pas de crash sur cart.produit_panier | Haute |
| T-24 | Banniere sans image | Pas d'erreur sur banniere.couverture.url | Haute |
| T-25 | About sans image | Pas d'erreur sur about.image.url | Haute |
| T-26 | Partenaire sans image | Pas d'erreur sur partenaire.image.url | Haute |
| T-27 | Galerie sans image | Pas d'erreur sur galerie.image.url | Moyenne |

---

## 4. Récapitulatif et plan d'exécution

### 4.1 Par priorité

| Priorité | Nombre de tests | Focus |
|----------|-----------------|-------|
| **Haute** | 52 | Robustesse (infos/cart vides), auth, panier, checkout, parcours critiques |
| **Moyenne** | 39 | Formulaires, APIs, context processors, edge cases |
| **Basse** | 3 | Newsletter, statiques, galerie produit |

**Total estimé : ~94 tests d'intégration**

### 4.2 Outils recommandés

- **Django Test Client** : `django.test.Client` pour simuler requêtes HTTP
- **TestCase** : `django.test.TestCase` (transaction rollback entre tests)
- **Factory Boy** ou **fixtures** : Données de test (User, Customer, Produit, Panier, etc.)
- **Selenium** ou **Playwright** : Tests E2E navigateur (parcours Vue.js, formulaires dynamiques)
- **pytest-django** : Alternative à unittest, fixtures, markers

### 4.3 Ordre d'implémentation suggéré

1. **Phase 1 - Critiques** : T-22, T-23, T-24, T-25, T-26 (robustesse infos/cart/images)
2. **Phase 2 - Auth** : C-01 à C-07, C-08 à C-13
3. **Phase 3 - Shop** : W-01 à W-04, S-01 à S-22
4. **Phase 4 - APIs panier** : C-19 à C-26
5. **Phase 5 - Client & Contact** : CL-01 à CL-11, CO-01 à CO-07
6. **Phase 6 - Parcours E2E** : T-09 à T-16
7. **Phase 7 - Transversal** : T-01 à T-08, T-17 à T-21

### 4.4 Données de test minimales

Pour exécuter les tests, prévoir :
- **SiteInfo** (1 enregistrement, champs requis)
- **User** + **Customer** (client)
- **User** + **Etablissement** (établissement)
- **CategorieEtablissement** + **CategorieProduit**
- **Produit** (avec/sans promo, avec/sans image)
- **Panier** + **ProduitPanier**
- **Banniere**, **About**, **Partenaire**, **Appreciation** (avec/sans images)
- **CodePromotionnel**
- **Contact**, **NewsLetter**
- **Commande** + **ProduitPanier** (commande)

---

*Document généré à partir de l'analyse ergonomique du projet SK_PROJTESTFINAL.*
