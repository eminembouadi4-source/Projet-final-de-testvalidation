# Tests statiques – CoolDeal (SK_PROJTESTFINAL)

**Objectif :** définir les contrôles “statiques” (sans exécuter les parcours métier) à mettre en place pour améliorer la **qualité**, la **robustesse**, la **sécurité** et la **cohérence** du projet, à partir de `analyse_de_projet.md`.

**Portée :**
- Analyse statique du code Python/Django.
- Vérifications configuration (settings, dépendances, secrets).
- Validation statique HTML/templates, CSS/JS, liens/URLs.

---

## 1) Analyse statique Python (qualité + erreurs probables)

### 1.1 Linting Python (style + erreurs)
**Outils recommandés**:
- `ruff` (lint + règles d’erreurs)
- `flake8` (option)

**Règles/cas à détecter (liés à l’analyse):**
- `except:` trop larges (ex: `website.context_processors.site_infos`, `cart`, `customer.views.islogin`, etc.)
- Variables inutilisées (ex: `_ = isSuccess`)
- Imports en double (ex: `from django.shortcuts import render` 2 fois)
- Noms ambigus / shadowing (ex: `models` importé depuis plusieurs apps)
- Complexité / fonctions trop longues (ex: `shop.views` contient beaucoup de logique)

### 1.2 Typage / cohérence des retours
**Outils**:
- `mypy` (optionnel, utile même partiel)

**Contrôles ciblés:**
- **Context processor `cart`** renvoie parfois `""` (string) au lieu d’un `Panier` -> risque `AttributeError` en template.
- Fonctions qui peuvent renvoyer `None` sans que les appels suivants le gèrent (`infos=None`, images null).

### 1.3 Détection de bugs probables
**Outils**:
- `pylint` (option, plus strict)

**Contrôles ciblés:**
- Accès direct à `request.FILES['file']` (risque `KeyError`) dans `customer.views.inscription`.
- Accès `.url` sur images `null=True` dans templates (à analyser côté templates aussi).

---

## 2) Analyse statique Django (configuration + checks)

### 2.1 `manage.py check`
**Objectif:** détecter erreurs Django (apps, urls, modèles, migrations).

Contrôles importants:
- Configuration des `context_processors`.
- Modèles/migrations cohérents.

### 2.2 Vérification Graphene
Dans `settings.py`, `GRAPHENE = {"SCHEMA": "cooldeal.schema.schema"}`.

**Tests statiques à faire:**
- Vérifier existence du module `cooldeal/schema.py` et de l’objet `schema`.
- Si absent, décider:
  - ajouter le fichier, ou
  - retirer Graphene de `INSTALLED_APPS` et `GRAPHENE`.

### 2.3 Analyse des URLs / reverse
**Outils**:
- `django-extensions` (optionnel) / inspection des `urls.py`.
- Contrôle statique via grep.

**Points issus de l’analyse:**
- Typos URL: `customer/urls.py` mentionne `cart/udpate/product` vs `cart/update/product`.
- Liens template vers `#`.

---

## 3) Analyse statique de sécurité

### 3.1 Secrets en clair (priorité haute)
**Outils**:
- `detect-secrets` (Yelp) ou `gitleaks`.

**Contrôles à faire (confirmés dans l’analyse):**
- `SECRET_KEY` en clair.
- `EMAIL_HOST_PASSWORD` en clair dans `settings.py`.

### 3.2 Bonnes pratiques Django
**Outils**:
- `bandit` (Python security linter)
- `django-secure-checklist` (manuel) / `pip-audit` (dépendances)

**Contrôles ciblés:**
- `DEBUG` et bascule par variable d’environnement.
- `ALLOWED_HOSTS` (ajouter `localhost` en dev si nécessaire).
- Paramètres `CSRF`, cookies, headers (checklist).

---

## 4) Analyse statique des dépendances

### 4.1 Audit vulnérabilités
**Outils**:
- `pip-audit`
- `safety` (option)

**Contrôles ciblés:**
- Version de libs anciennes côté front (jQuery 1.12.0 mentionné).
- Paquets problématiques:
  - `cinetpay-sdk` non disponible sur PyPI -> imports optionnels: vérifier cohérence.

### 4.2 Cohérence `requirements.txt` / lock
**Tests statiques:**
- Vérifier qu’un fichier de dépendances existe et liste tout ce qui est importé:
  - `graphene_django`, `cities_light`, `whitenoise`, `django_cron`, `playwright`, etc.

---

## 5) Analyse statique templates Django / HTML

### 5.1 Validation HTML
**Outils**:
- Validateur W3C (manuel) ou `html5validator`.

**Contrôles ciblés (analyse):**
- `lang="en"` alors que le site est en français -> cohérence.
- Attribut favicon: `type="images/x-icon"` doit être `image/x-icon`.
- Présence de `<label>` associés aux champs (accessibilité minimale).

### 5.2 Contrôle de robustesse templates (variables None)
**Objectif:** détecter usages dangereux:
- `infos.icon.url`, `infos.logo.url` quand `infos is None`.
- `banniere.couverture.url`, `partenaire.image.url`, `about.image.url` quand image `null=True`.
- `cart.produit_panier.count` quand `cart` n’est pas un objet `Panier`.

**Méthodes:**
- Grep sur `.url` et ajouter une revue systématique.
- Si vous utilisez `django.template` en CI, activer un mode strict ou écrire un script de rendu minimal (semi-statique).

### 5.3 Cohérence marque / langue
**Contrôles à faire:**
- Recherche globale de `Beautyhouse` dans templates.
- Recherche globale de libellés anglais (ex: `HOME`, `Submit`, `Search here...`).

---

## 6) Analyse statique JS/CSS

### 6.1 Lint JavaScript
**Outils**:
- `eslint` (si build front) ou au minimum revue statique.

**Contrôles ciblés:**
- Code Vue.js dupliqué (login/contact/panier) -> détecter répétitions.
- Appels AJAX vers endpoints Django: vérifier que les URLs existent.

### 6.2 Lint CSS
**Outils**:
- `stylelint`.

**Contrôles ciblés:**
- Styles inline répétitifs (`style="color: white;"`).
- Tailles fixes (ex `font-size: 16px`) -> cohérence responsive.

---

## 7) Analyse statique des liens et routes

### 7.1 Liens cassés / placeholders
**Contrôles issus de l’analyse:**
- Liens partenaires pointent vers `#`.
- Icône panier sur desktop pointe vers `#`.

**Test statique à faire:**
- Scanner templates pour `href="#"` et lister toutes les occurrences.

### 7.2 Pages d’erreur
**Contrôles:**
- `404.html` contient typos et `href="index.html"` au lieu d’un `{% url %}`.

---

## 8) Priorisation (recommandée)

### Priorité haute
- Secrets en clair (`SECRET_KEY`, SMTP password) via `detect-secrets`/`gitleaks`.
- Robustesse templates: usages `.url` sur champs optionnels + `infos/cart` potentiellement `None`/string.
- Graphene schema manquant (import statique).
- Typos routes (`udpate`).

### Priorité moyenne
- Lint Python (ruff/flake8), duplication imports, `except:` trop larges.
- Audit dépendances (`pip-audit`).
- Cohérence marque/langue (recherche globale).

### Priorité basse
- Lint CSS/JS et règles de style (à faire quand pipeline front est stabilisé).

---

## 9) Livrables attendus (CI recommandé)

- Un job CI “**static checks**” qui exécute:
  - `ruff` (et/ou `flake8`)
  - `bandit`
  - `pip-audit`
  - `detect-secrets` (ou `gitleaks`)
  - (option) validation HTML sur un échantillon de pages/templates
