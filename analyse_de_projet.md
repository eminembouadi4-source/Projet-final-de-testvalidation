# Analyse ergonomique du projet SK_PROJTESTFINAL (CoolDeal)

**Date d'analyse :** 1er février 2026  
**Projet :** Plateforme de deals et réservations – Côte d'Ivoire  
**Stack technique :** Django 4.2, Python, Bootstrap, Vue.js, jQuery

---

## 1. Vue d'ensemble du projet

### 1.1 Architecture

Le projet **CoolDeal** est une application web Django de type e-commerce/B2B orientée deals, produits et services en Côte d'Ivoire. Il s'organise autour de plusieurs applications :

| Application | Rôle | URLs principales |
|-------------|------|------------------|
| **website** | Page d'accueil, À propos | `/`, `/a-propos` |
| **shop** | Catalogue deals, panier, checkout, dashboard établissements | `/deals/`, `/deals/cart`, `/deals/checkout` |
| **customer** | Auth, inscription, panier, paiement | `/customer/`, `/customer/signup` |
| **client** | Espace client (profil, commandes, favoris) | `/client/`, `/client/commande` |
| **contact** | Formulaire de contact | `/contact/` |
| **base** | Templates de base | — |
| **site_config** | Configuration du site | — |

### 1.2 Structure des URLs

- **Racine** : Accueil, à propos
- **/deals/** : Boutique et produits (shop)
- **/customer/** : Authentification et gestion panier
- **/client/** : Espace utilisateur connecté
- **/contact/** : Contact
- **/admin/** : Administration Django (django-daisy)

---

## 2. Analyse de l'ergonomie

### 2.1 Navigation et structure

#### Points positifs
- Navigation principale claire : Accueil, Deal, A Propos, Contact
- Menu déroulant pour les catégories de deals
- Fil d'Ariane (breadcrumbs) sur les pages internes
- Séparation nette entre utilisateurs clients et établissements
- Accès rapide au panier visible dans le header

#### Points à améliorer
- **Incohérence mobile** : Sur mobile, le lien « Panier » est dans le menu, mais sur desktop l’icône panier pointe vers `#` au lieu de `{% url 'cart' %}`
- **Utilisateur connecté (mobile)** : Le nom d’utilisateur n’a pas de lien vers le profil
- **Recherche** : L’icône de recherche ne déclenche aucune action utile (recherche non fonctionnelle)
- **Liens partenaires** : Tous pointent vers `#` (aucune URL réelle)

### 2.2 Cohérence et identité visuelle

#### Problèmes identifiés
1. **Marque incohérente** : Les titres de pages utilisent « Beautyhouse » alors que le projet s’appelle « CoolDeal »
   - `index.html` : `Beautyhouse | Home`
   - `login.html` : `Beautyhouse | Login`
   - `shop.html` : `Beautyhouse | Shop`
   - etc.

2. **Langue** : Mélange anglais/français (ex. « HOME » vs « Accueil » dans les breadcrumbs)

3. **Footer** : Copyright « Cool Deal 2023 » (année à mettre à jour)

### 2.3 Formulaires

#### Points positifs
- Validation côté client (Vue.js) sur login et contact
- Messages de succès/erreur
- Gestion du token CSRF

#### Points à améliorer
1. **Formulaire contact** : `action="https://whizthemes.com/nazmul/php/mail.php"` – URL externe incohérente (le traitement réel est en AJAX vers Django)
2. **Labels et accessibilité** : Peu de `<label>` associés aux champs
3. **Placeholder en anglais** : « Search here... » dans le header
4. **Boutons** : Texte « Submit » au lieu de « Connexion » ou « Envoyer » selon le contexte
5. **Typo** : « Vous n'avez-pas » → « Vous n'avez pas »

### 2.4 Robustesse et gestion des erreurs

#### Risques identifiés
1. **Variable `infos`** : Si aucun `SiteInfo` n’existe en base, `infos` est `None` et le template peut lever des erreurs (ex. `infos.icon.url`, `infos.logo.url`, etc.)

2. **Variable `cart`** : Le context processor peut renvoyer `cart = ""` en cas d’exception. Appeler `cart.produit_panier.count` sur une chaîne provoque une erreur.

3. **Images optionnelles** : `banniere.couverture`, `partenaire.image`, `about.image` peuvent être null, mais `.url` est utilisé sans vérification.

4. **Favicon** : `type="images/x-icon"` incorrect (doit être `image/x-icon`).

### 2.5 Accessibilité

#### Points positifs
- `lang="en"` dans le HTML (à adapter en `fr` pour un site en français)
- Viewport meta tag pour le responsive
- Utilisation d’icônes Material Design (zmdi)

#### Points à améliorer
- Attributs `alt` parfois vides ou peu descriptifs
- Dropdown basé sur `:hover` uniquement (peu adapté au clavier et au tactile)
- Contraste à vérifier sur les textes blancs sur fond sombre
- Absence de `aria-label` sur les icônes et boutons

### 2.6 Responsive design

#### Points positifs
- Bootstrap utilisé (grilles responsive)
- Fichier `responsive.css` avec breakpoints (992px, 768px, etc.)
- Menu mobile (`d-lg-none`) distinct du menu desktop
- Images responsives via classes Bootstrap

#### Points à améliorer
- Tailles de police fixes (ex. `font-size: 16px`) à envisager en unités relatives
- Possibles débordements sur petits écrans pour les tableaux (panier, commandes)
- Menu mobile à tester sur différentes tailles d’écran

### 2.7 Parcours utilisateur

#### Parcours type
1. Accueil → Découverte des deals  
2. Clic sur « Découvrir » ou catégorie  
3. Liste des produits → Fiche produit  
4. Ajout au panier → Panier → Checkout  
5. Connexion/inscription si nécessaire  
6. Paiement (CinetPay)

#### Observations
- Le panier est accessible sans connexion (sessions anonymes)
- Logique client / établissement bien séparée
- Pas de retour explicite vers la boutique après checkout

### 2.8 Performance

- WhiteNoise pour les fichiers statiques
- Compression des assets (STATICFILES_STORAGE)
- jQuery 1.12.0 utilisé (version ancienne, à envisager de mettre à jour)
- Beaucoup de scripts chargés sur toutes les pages (peut ralentir le premier chargement)

---

## 3. Problèmes techniques identifiés

### 3.1 Erreurs et typos

| Fichier | Problème | Correction suggérée |
|---------|----------|---------------------|
| `product-details.html` | « Dteials », « Proudct », « Prouduct » | Details, Product |
| `404.html` | « rong », « currect » | wrong, correct |
| `404.html` | Lien `href="index.html"` | `href="{% url 'index' %}"` |
| `customer/urls.py` | `cart/udpate/product` | `cart/update/product` |
| `base.html` | `type="images/x-icon"` | `type="image/x-icon"` |
| `index.html` | Point superflu après lien partenaire `</a>.` | `</a>` |

### 3.2 Configuration

- **Graphene** : Référence à `cooldeal.schema.schema` alors qu’aucun fichier `schema.py` n’est présent
- **cinetpay-sdk** : Non disponible sur PyPI ; import rendu optionnel
- **ALLOWED_HOSTS** : `localhost` absent (utile en développement local)
- **SECRET_KEY** : Présente en clair (à externaliser en production)
- **Credentials email** : Mot de passe SMTP en clair dans `settings.py`

### 3.3 Duplication de code

- Doublons `class="breadcrumbs text-center"` dans plusieurs templates
- Logique Vue.js répétée entre login, contact, panier, etc.
- Styles inline (`style="color: white;"`) à regrouper en classes CSS

---

## 4. Recommandations prioritaires

### Priorité haute
1. Corriger les variables `infos` et `cart` pour éviter les erreurs quand elles sont vides
2. Remplacer « Beautyhouse » par « CoolDeal » partout
3. Corriger le lien du panier (icône → `{% url 'cart' %}`)
4. Corriger la page 404 (orthographe et lien d’accueil)
5. Ajouter ou adapter le fichier `schema.py` pour Graphene, ou retirer Graphene si non utilisé

### Priorité moyenne
1. Uniformiser la langue (français ou anglais)
2. Améliorer les labels et l’accessibilité des formulaires
3. Corriger le formulaire de contact (action, libellés des boutons)
4. Corriger les typos dans les templates
5. Gérer les images null avant l’appel à `.url`

### Priorité basse
1. Harmoniser les breadcrumbs (HOME vs Accueil)
2. Mettre à jour le copyright (2023 → année courante)
3. Remplacer les liens `#` par des URLs réelles
4. Implémenter la recherche ou retirer l’icône
5. Mettre à jour jQuery et revoir le chargement des scripts

---

## 5. Synthèse

### Forces du projet
- Architecture Django claire et modulaire
- Bonne séparation client / établissement
- Panier utilisable sans compte
- Utilisation de Vue.js pour des formulaires réactifs
- Mise en page responsive (Bootstrap)
- Fil d’Ariane sur les pages internes

### Axes d’amélioration
- Robustesse : gestion des données manquantes (infos, cart, images)
- Cohérence : marque, langue, libellés
- Qualité : typos, liens cassés, configuration
- Accessibilité et UX : labels, navigation clavier, contrastes
- Sécurité : externalisation des secrets (SECRET_KEY, SMTP)

### Score ergonomie (estimation)

| Critère | Note /10 | Commentaire |
|---------|----------|-------------|
| Navigation | 7 | Claire mais liens panier et recherche à corriger |
| Cohérence visuelle | 5 | Incohérence Beautyhouse / CoolDeal |
| Formulaires | 6 | UX correcte, accessibilité et libellés à améliorer |
| Robustesse | 4 | Risques d’erreurs avec infos/cart vides |
| Accessibilité | 5 | À améliorer (alt, aria, clavier) |
| Responsive | 7 | Bonne base Bootstrap |
| **Global** | **5,7/10** | Base solide, corrections ciblées nécessaires |

