# Projet 8INF349 – Paiement en ligne (Docker)

Ce dépôt contient l'application Flask développée pour le projet de session du cours 8INF349, avec un déploiement via Docker et Docker Compose.

## Lancement rapide avec Docker

### Prérequis

- Docker
- Docker Compose
- `make` (facultatif mais recommandé)

## Commandes utiles

### Démarrer l’application

```bash
make run
```

### Initialiser la base de données

```bash
make init-db
```

### Voir les logs du conteneur Flask

```bash
make logs
```

### Arrêter l’application

```bash
make stop
```

### Nettoyer complètement (conteneurs + volumes + cache)

```bash
make clean
```

## Contenu du `docker-compose.yml`

- web (Flask, Python 3.10, Peewee, psycopg2-binary)
- postgres (PostgreSQL 12 avec volume persistant)
- redis (Redis 5)

Les services exposent :

- localhost:5000 → Flask API
- localhost:5432 → PostgreSQL
- localhost:6379 → Redis

## Variables d’environnement configurées automatiquement

- `FLASK_APP=inf349.py`
- `REDIS_URL=redis://redis:6379`
- `DB_HOST=postgres`
- `DB_USER=postgres`
- `DB_PASSWORD=postgres`
- `DB_PORT=5432`
- `DB_NAME=api8inf349`
