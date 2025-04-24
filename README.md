# Projet 8INF349 – Paiement en ligne (Docker)

Ce dépôt contient l'application Flask développée pour le projet de session du cours 8INF349, avec un déploiement via Docker et Docker Compose.

## Lancement rapide avec Docker

### Prérequis

- Docker
- Docker Compose
- `make` (facultatif mais recommandé)

## Commandes utiles

- Démarrer et initialiser l’application "from scratch": `make run`
- Voir les logs du conteneur Flask: `docker logs -f api8inf349`

Contenu du `docker-compose.yml`:
- postgres (PostgreSQL 12 avec volume persistant)
- redis (Redis 5)

Les services exposent :
- localhost:5432 → PostgreSQL
- localhost:6379 → Redis
