# Plan de tests unitaires – CoolDeal (SK_PROJTESTFINAL)

**Objectif :** lister les tests unitaires à implémenter à partir des risques/fonctionnalités identifiés dans `analyse_de_projet.md` et du code Django existant.

**Portée :** tests unitaires Python/Django (models, propriétés, context processors, fonctions de vues qui manipulent de la logique). Les tests d’IHM/templates (typos, libellés, "Beautyhouse"), responsive, et accessibilité relèvent plutôt de tests d’intégration/recette et ne sont pas détaillés ici.

---

## 1) Pré-requis et conventions de test

- **Framework**: `pytest-django` ou `django.test.TestCase` (au choix).
- **Isolation**:
  - Mock des dépendances externes (`send_mail`, Playwright, CinetPay, Graphene si présent).
  - Pas d’appel réseau réel.
- **Données**:
  - Utiliser `User` Django + création de `Customer` quand requis.
  - Pour `cities_light.City`, soit créer un objet `City` en base de test, soit mocker l’accès.

---

## 2) Tests unitaires – `website.context_processors`

Fichier: `cod_test/website/context_processors.py`

### 2.1 `categories(request)`
- **Retour nominal**: renvoie un dict avec la clé `cat` contenant uniquement les catégories `status=True`.
- **Filtrage**: vérifier qu’une catégorie `status=False` n’apparaît pas.
- **Type de retour**: `cat` doit être un `QuerySet` (ou au moins itérable de modèles) et non `None`.

### 2.2 `site_infos(request)`
- **Nominal**: si au moins un `SiteInfo` existe, renvoie le plus récent (`latest('date_add')`).
- **Cas vide**: si aucun `SiteInfo` n’existe, renvoie `{'infos': None}` sans exception.
- **Robustesse**: ne doit jamais lever d’exception même si la table est vide.

### 2.3 `cities(request)`
- **Nominal**: renvoie `{'cities': City.objects.all()}`.
- **Stabilité**: si aucune ville, `cities` est vide mais défini.

### 2.4 `galeries(request)`
- **Nominal**: ne renvoie que `status=True`.
- **Limite**: renvoie au maximum 6 éléments (`[:6]`).

### 2.5 `horaires(request)`
- **Nominal**: ne renvoie que `status=True`.

### 2.6 `cart(request)` (priorité haute)
Risque principal mentionné dans l’analyse: `cart` peut être une chaîne vide ou un objet `Panier`.

Cas à couvrir:
- **Session inexistante**: si `request.session.session_key` absent, la session est créée et un `Session` Django existe.
- **Utilisateur anonyme**:
  - **Panier existant**: récupère `Panier` par `session_id`.
  - **Panier inexistant**: crée un `Panier` lié à `session_id`.
- **Utilisateur authentifié**:
  - **Customer existant + panier existant**: récupère `Panier(customer=..., session_id=...)`.
  - **Customer existant + panier inexistant**: crée un `Panier` lié à `customer` et `session_id`.
  - **Customer manquant**: doit être clarifié (actuellement `Customer.objects.get(user=request.user)` est appelé et peut lever). Tester l’exception attendue, ou décider d’un correctif.
- **Robustesse**:
  - Le context processor doit toujours renvoyer un dict avec `cart` défini.
  - Vérifier qu’en cas d’exception interne, la valeur actuelle `""` est renvoyée (comportement actuel).

---

## 3) Tests unitaires – `website.models`

Fichier: `cod_test/website/models.py`

### 3.1 `SiteInfo.__str__`
- **Nominal**: retourne `titre`.

### 3.2 Modèles avec images optionnelles (`Banniere`, `About`, `Galerie`, `Partenaire`)
- **Création**: création possible avec `image`/`couverture` à `None` quand `null=True`.
- **Contraintes**: vérifier la présence/absence de `null=True` sur les champs mentionnés à risque dans l’analyse.

---

## 4) Tests unitaires – `customer.models`

Fichier: `cod_test/customer/models.py`

### 4.1 Import optionnel CinetPay
- **Sans package**: si `cinetpay_sdk` non installé, `Cinetpay` doit valoir `None` et l’import ne doit pas échouer.

### 4.2 `Customer.__str__`
- **Nominal**: retourne `user.username`.

### 4.3 `PasswordResetToken.is_valid()`
- **Nominal**: token créé maintenant -> `True`.
- **Expiré**: token avec `created_at` (maintenant - 1h - epsilon) -> `False`.
- **Bord**: exactement 1 heure -> `True` (selon l’implémentation `<= timedelta(hours=1)`).

### 4.4 `Panier.total`
- **Panier vide**: total = 0.
- **Sans promo**: somme des `ProduitPanier.total`.
- **Avec promo**: vérifier que `ProduitPanier.total` prend en compte `produit.check_promotion`.
- **Arrondi/type**: retour `int`.

### 4.5 `Panier.total_with_coupon`
- **Sans coupon**: `total_with_coupon == total`.
- **Avec coupon**: réduction = `coupon.reduction * total`.
- **Bords**:
  - `reduction=0`.
  - `reduction` élevée (ex: 1.0) -> total réduit à 0 (ou négatif) : tester le comportement attendu (actuellement peut devenir négatif).
- **Type**: retour `int`.

### 4.6 `Panier.check_empty`
- **Vide**: aucun `ProduitPanier` -> `False`.
- **Non vide**: au moins 1 -> `True`.

### 4.7 `Commande.check_paiement`
- **Comportement actuel**: renvoie toujours `True`.
- **Test de non-régression**: un test simple qui valide ce comportement (ou décider d’une implémentation réelle ensuite).

### 4.8 `ProduitPanier.total`
- **Promo active**: retourne `prix_promotionnel * quantite`.
- **Sans promo**: retourne `prix * quantite`.
- **Quantité**:
  - `quantite=1`.
  - `quantite>1`.

---

## 5) Tests unitaires – `customer.views`

Fichier: `cod_test/customer/views.py`

### 5.1 Pages de formulaire simples (`login`, `signup`, `forgot_password`)
- **Utilisateur déjà connecté**: redirection vers `index`.
- **Utilisateur anonyme**: code 200 + template attendu.

### 5.2 `islogin(request)` (auth AJAX)
- **Username = email**:
  - email existant + mot de passe correct -> JSON `success=True`.
  - email existant + mot de passe faux -> JSON `success=False`.
  - email inexistant -> JSON `success=False`.
- **Username = username**:
  - user existant + mdp correct -> `success=True`.
  - user existant + mdp faux -> `success=False`.
- **Compte inactif**: `user.is_active=False` -> `success=False`.
- **Payload invalide**:
  - JSON invalide / clés manquantes -> réponse `success=False` (comportement actuel: `except:` global).

### 5.3 `inscription(request)` (création compte)
Cas nominaux:
- **Création OK**: champs requis valides -> user créé + customer créé + JSON `success=True`.

Cas d’erreur:
- **Email invalide** -> `success=False`.
- **Passwords différents** -> `success=False`.
- **Username/email déjà utilisé** -> `success=False`.
- **Ville**:
  - ville fournie -> `Customer.ville` correctement assignée.
  - ville absente -> `Customer.ville is None`.
- **Fichier photo**:
  - pas de fichier -> ne doit pas lever.
  - fichier présent -> `Customer.photo` assignée.

Note: le code actuel fait `if request.FILES['file']:` (KeyError si absent). Un test doit capturer ce bug potentiel (et/ou amener à un correctif).

### 5.4 `add_to_cart(request)`
- **Ajout premier produit**: crée `ProduitPanier` si inexistant.
- **Ajout produit existant**: met à jour `quantite` sur l’existant.
- **Paramètres manquants**: `success=False`.
- **IDs invalides**: `Panier` ou `Produit` inexistants -> comportement actuel (exception non gérée) : tester l’exception ou prévoir un correctif.

### 5.5 `delete_from_cart(request)`
- **Suppression OK**: supprime `ProduitPanier` existant.
- **Paramètres manquants**: `success=False`.

### 5.6 `add_coupon(request)`
- **Coupon valide**: associe le `CodePromotionnel` au `Panier`.
- **Coupon invalide**: `success=False`.
- **Paramètres manquants**: `success=False`.

### 5.7 `update_cart(request)`
- **Update OK**: modifie `quantite` du `ProduitPanier`.
- **Paramètres manquants**: `success=False`.
- **ProduitPanier manquant**: comportement actuel (exception) : test attendu ou correctif.

### 5.8 Reset password
#### 5.8.1 `request_reset_password(request)`
- **GET**: retourne template `reset_password/request.html`.
- **POST email invalide**: message erreur.
- **POST email inexistant**: message erreur.
- **POST email OK**:
  - crée (ou met à jour) `PasswordResetToken`.
  - génère un token de longueur 64.
  - appelle `send_mail` avec une URL contenant le token.
  - redirige.

(Mock requis: `send_mail`, et éventuellement `request.build_absolute_uri`.)

#### 5.8.2 `reset_password(request, token)`
- **Token inexistant**: redirection + message.
- **Token expiré**: suppression du token + redirection.
- **GET token valide**: retourne template `reset_password/reset.html`.
- **POST mots de passe différents**: message erreur.
- **POST OK**:
  - modifie le password utilisateur.
  - supprime le token.
  - redirige vers `login`.

### 5.9 `test_email(request)`
- **Success**: `send_mail` appelé -> JSON status success.
- **Failure**: `send_mail` lève -> JSON status error.

---

## 6) Tests unitaires – `shop.views`

Fichier: `cod_test/shop/views.py`

### 6.1 `shop(request)`
- **Nominal**: fournit `produits` filtrés `status=True`.

### 6.2 `product_detail(request, slug)`
- **Produit existant**: code 200 + contexte contient `produit`.
- **Produits similaires**: max 3, même catégorie, exclut le produit courant.
- **Favoris**:
  - user anonyme -> `is_favorited=False`.
  - user connecté + favori existant -> `True`.

### 6.3 `toggle_favorite(request, produit_id)`
- **Non connecté**: redirection `login` + message.
- **Connecté**:
  - favori inexistant -> création.
  - favori existant -> suppression.

### 6.4 `paiement_success(request)`
- **Connecté**: rend `paiement.html` avec `commandes` de `request.user.customer`.
- **Non connecté**: redirection `index`.

### 6.5 `single(request, slug)`
- **Slug CategorieProduit**: renvoie produits associés.
- **Slug CategorieEtablissement**: renvoie produits associés.
- **Slug inconnu**: redirection `shop`.

### 6.6 `post_paiement_details(request)` (priorité haute)
- **Paramètres OK** + panier appartenant au user:
  - crée une `Commande`.
  - transfère les `ProduitPanier` du `panier` vers la `commande`.
  - supprime le panier.
  - renvoie JSON `success=True`.
- **Panier non trouvé / n’appartient pas à user**: `success=False`.
- **User non authentifié**: `success=False`.
- **Robustesse transactionnelle**: si exception pendant la création commande:
  - `success=False`.
  - vérifier qu’aucun produit n’a été détaché partiellement (actuellement pas de transaction; test pour révéler le risque).

### 6.7 Dashboard établissement (views `dashboard`, `ajout_article`, `article_detail`, `modifier_article`, `supprimer_article`, `commande_reçu*`, `etablissement_parametre`)
Ces vues contiennent de la logique métier testable:

- **Permissions**:
  - accès nécessite `login_required`.
  - `get_object_or_404(Etablissement, user=request.user)` -> 404 si pas d’établissement.
- **`dashboard`**:
  - calcule `total_articles`.
  - calcule `commandes_aujourdhui` (filtre date).
  - calcule `total_commandes`.
- **`modifier_article`**:
  - conversion prix `"1,5"` -> `1.5`.
  - prix invalide -> message erreur + redirection.
- **`commande_reçu`**:
  - filtres `client`, `produit`, `status`, `date_min/date_max`.
  - pagination.

---

## 7) Tests unitaires – `client.views`

Fichier: `cod_test/client/views.py`

### 7.1 Accès / redirections liées à `Customer`
- **`profil`/`commande`/`commande_detail`/`suivie_commande`/`souhait`/`avis`**:
  - si `request.user.customer` absent -> redirection `index` (comportement actuel via `try/except`).
  - si présent -> code 200 + template.

### 7.2 `commande(request)` (recherche + pagination)
- **Sans query**: renvoie toutes commandes.
- **Avec `q`**: filtre sur transaction_id, date, nom produit.
- **Pagination**: 10 par page.
- **Données agrégées**: `commandes_data` contient bien la liste des produits par commande.

### 7.3 `parametre(request)`
- **GET**: template + contexte.
- **POST**: met à jour `User` et `Customer`.
- **Ville**: id fourni -> assignation, sinon `None`.
- **Photo**: upload facultatif.

### 7.4 `invoice_pdf(request, order_id)` (priorité haute)
Dépendances externes lourdes (Playwright, rendu HTML, QR code, accès à `SiteInfo.latest`).

- **Sécurité**:
  - si `request.user` n’a pas de `customer` -> redirection `commande`.
  - si commande n’appartient pas au customer -> redirection `commande`.
- **Nominal**:
  - mocker `sync_playwright()` pour éviter lancement navigateur.
  - mocker `SiteInfo.objects.latest`.
  - vérifie que la réponse est un `HttpResponse` avec `content_type="application/pdf"`.
  - vérifie `Content-Disposition` contient `Recu_<transaction_id>.pdf`.

---

## 8) Tests unitaires – configuration / intégrations mentionnées

### 8.1 Graphene (settings `GRAPHENE["SCHEMA"] = "cooldeal.schema.schema"`)
- **Import du schema**:
  - test que `import cooldeal.schema` fonctionne si le fichier existe.
  - si le fichier est absent, test qui échoue volontairement pour signaler la dette technique (ou retirer Graphene).

### 8.2 Sécurité / settings (non-fonctionnel)
- Pas unitaire: la présence de secrets en clair est un point de sécurité (à corriger via env vars), pas un test unitaire.

---

## 9) Priorisation (recommandée)

### Priorité haute (risque crash / paiement)
- `website.context_processors.cart`.
- `website.context_processors.site_infos`.
- `customer.models.Panier` (total / coupon / empty).
- `shop.views.post_paiement_details`.
- `customer.views.reset_password` / `request_reset_password` (avec mocks).
- `client.views.invoice_pdf` (avec mocks Playwright/SiteInfo).

### Priorité moyenne
- Auth AJAX `customer.views.islogin`.
- CRUD panier (`add_to_cart`, `update_cart`, `delete_from_cart`, `add_coupon`).
- Favoris (`shop.views.toggle_favorite`).
- Pages boutique (`shop`, `product_detail`, `single`).

### Priorité basse
- Tests simples `__str__` et modèles sans logique.

---

## 10) Remarques importantes (tests qui révèlent des bugs)

- **`inscription`**: `request.FILES['file']` peut lever `KeyError` si aucun fichier n’est envoyé. Prévoir un test qui le met en évidence.
- **`post_paiement_details`**: inversion probable `return_url`/`notify_url` + absence de transaction DB (risque de transfert partiel). Prévoir des tests pour détecter la régression.
- **Context processor `cart`**: en cas d’exception globale, renvoie `cart=""` (string) -> risque de crash template si on accède à `cart.produit_panier`. Les tests doivent pousser à harmoniser le type renvoyé.
