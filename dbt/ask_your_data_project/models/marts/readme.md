# 🚀 Marts : Tables, Jointures et Logique Métier

## 🗂️ Présentation

La couche **marts** rassemble les **tables d’analyse métier** du projet Olist

---

## ⚡ Transformations et Jointures par Modèle

### 🧑‍💼 `dim_customers.sql`
Jointure entre `stg_customers` et `brazilian_states`.  
👉 *Cette jointure ajoute la région (`customer_region`) pour chaque client, ce qui permet d’analyser la distribution géographique des clients et de créer des indicateurs régionaux.*

### 🏪 `dim_sellers.sql`
Jointure entre `stg_sellers` et `brazilian_states`.  
👉 *La jointure permet d’obtenir le champ `seller_region` pour chaque vendeur, facilitant l’analyse des ventes et leur répartition régionale.*

### 📦 `dim_products.sql`
Jointure entre `stg_products` et `product_category_translation` (version anglaise de la catégorie produit).  
👉 *Cette jointure améliore la lisibilité pour des analyses ou applications multilingues.*

### 📝 `fact_orders.sql`
Jointure entre `stg_orders` et `calendar`.  
👉 *La jointure enrichit chaque commande par des attributs temporels (année, mois, jour, week-end…), ce qui facilite l’analyse par période et la saisonnalité.*

### 📦 `fact_order_items.sql`
Jointure entre `stg_order_items` et `calendar`.  
👉 *Cette jointure crée le champ `shipping_limit_date_key` pour chaque article de commande, permettant l’analyse logistique et le suivi des expéditions dans le temps.*

---

## 🔒 Tests et Documentation YAML dans Marts

Les fichiers YAML servent à :
- **📝 Documentation** : chaque table et colonne est décrite pour faciliter l’onboarding et la navigation dans dbt docs.
- **✅ Tests automatiques** :
  - `not_null` : aucune clé fondamentale manquante.
  - `unique` : pas de doublon sur les identifiants clés.
  - `relationships` : intégrité entre les tables (FK existantes, ex: chaque `customer_id` des facts doit exister dans sa dim).

---

## ⚙️ Graphe de Transformation dbt Docs

Le graphe généré par dbt docs :
- 🛣️ **Montre la chaîne complète** depuis la source brute jusqu’à la table finale.
- 👀 **Prouve la traçabilité** et la modularité : tu peux enrichir/debug chaque étape sans casser le pipeline.
- 🗺️ **Facilite la maintenance et l’évolution du projet**.

---



