# Prédicteur de prix d’occasion (FR/AR)

Cette petite application web permet d’estimer rapidement le prix d’objets d’occasion (voiture, téléphone, ordinateur, montre, caméra, autre) en **dirhams marocains (DH)**, avec une interface disponible en **français** et en **arabe**, et un **mode clair / sombre**.

Elle est construite avec :

- Python 3
- Flask
- HTML + CSS (sans JavaScript obligatoire)

---

## 1. Installation

### Prérequis

- **Python 3.10+** installé (`python --version` dans un terminal).
- (Optionnel) **Git** si vous voulez versionner le projet.

### Récupérer le projet

Placez-vous dans le dossier où vous voulez cloner / copier le projet, par exemple sur le Bureau.

Si vous utilisez Git :

```bash
git clone <url_du_dépôt>
cd app
```

Sinon, copiez simplement les fichiers dans un dossier, par exemple `c:\Users\PC\Desktop\app`.

### Créer un environnement virtuel (recommandé)

Sous Windows :

```bash
cd app
python -m venv .venv
.venv\Scripts\activate
```

Sous Linux / macOS :

```bash
cd app
python -m venv .venv
source .venv/bin/activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 2. Lancer l’application

Dans le dossier du projet (`app`) avec l’environnement virtuel activé :

```bash
python app.py
```

Le serveur Flask démarre en mode développement.  
Par défaut, l’application est disponible à l’adresse :

```text
http://127.0.0.1:5000
```

Ouvrez cette URL dans votre navigateur.

Pour arrêter le serveur, utilisez `Ctrl + C` dans le terminal.

---

## 3. Fonctionnalités

### 3.1. Choix de la langue et du thème

En haut de la page :

- **Langue** : Français / العربية  
- **Thème** : Sombre / Clair

Après avoir choisi vos préférences, cliquez sur **Appliquer**.  
La page se recharge avec la langue et le thème sélectionnés.

### 3.2. Catégories prises en charge

- Voiture
- Téléphone
- Ordinateur
- Montre
- Caméra
- Autre

Quand vous cliquez sur une catégorie, le formulaire se met à jour automatiquement avec des champs adaptés (marque, modèle, année, etc.) et les champs sont vidés pour une nouvelle estimation.

### 3.3. Estimation

Pour chaque catégorie, vous renseignez quelques informations (par exemple : marque, modèle, année, état).  
L’application calcule ensuite un **prix estimé en DH** à partir :

- d’un prix neuf indicatif (interne au modèle, propre à chaque catégorie),
- de l’**âge** estimé à partir de l’année,
- d’une interprétation textuelle de l’**état** (neuf, comme neuf, bon, moyen, abîmé, etc.).

Le résultat indique :

- la **catégorie** (dans la langue choisie),
- le **prix estimé** arrondi (en DH),
- un **texte explicatif** rappelant que l’estimation est indicative.

> ⚠️ **Important**  
> Il s’agit d’une estimation approximative, purement pédagogique, **ce n’est pas une expertise professionnelle**.

---

## 4. Structure du projet

```text
app/
├─ app.py              # Backend Flask + logique d’estimation
├─ requirements.txt    # Dépendances Python (Flask)
├─ templates/
│  └─ index.html       # Page principale (FR/AR, thèmes, formulaires)
└─ static/
   └─ styles.css       # Styles globaux, dark/light, layout
```

---

## 5. Personnalisation

- Vous pouvez ajuster les **valeurs de base des catégories** et la logique de calcul dans `app.py` (`CATEGORY_BASE_PRICE` et la fonction `estimate_price`).
- Les textes (FR/AR) sont dans `templates/index.html`.
- Les couleurs et le comportement des thèmes clair/sombre sont définis dans `static/styles.css` via des variables CSS (`--bg-page`, `--text-main`, etc.).

---

## 6. Limitations et pistes d’amélioration

- Pas de véritable modèle de machine learning : les prix sont calculés via des règles simples.
- Les données réelles du marché ne sont pas utilisées.

Idées d’amélioration :

- connecter un vrai modèle ML entraîné sur des annonces,
- ajouter la persistance des préférences langue/thème (cookies),
- intégrer une API (par exemple pour récupérer des prix moyens d’occasion).

