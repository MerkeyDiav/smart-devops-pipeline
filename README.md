# Smart DevOps Pipeline with AI-Powered Security Analysis

Un pipeline CI/CD intelligent qui utilise l'IA (Amazon Bedrock) pour détecter automatiquement les mauvaises pratiques DevOps avant le déploiement.

## Concept

Ce projet démontre comment intégrer l'intelligence artificielle dans un pipeline DevOps pour améliorer la sécurité et la qualité du code. Au lieu de se fier uniquement aux scanners classiques, le pipeline utilise Amazon Nova Pro pour analyser le code comme le ferait un expert DevOps senior.

## Architecture

```
GitHub Push → GitHub Actions
    ↓
Phase 1: Scanners Classiques
    ├─ Trivy (Docker + secrets)
    ├─ TFLint (Terraform syntax)
    └─ Checkov (IaC security)
    ↓
Phase 2: AI Analysis (Amazon Bedrock Nova Pro)
    ├─ Terraform (IAM, Security Groups, encryption)
    ├─ Dockerfile (multi-stage, secrets, optimization)
    └─ Code (API keys, validation, error handling)
    ↓
Phase 3: Gatekeeper Decision
    └─ BLOCK / WARN / PASS
    ↓
Phase 4: Reports & Notifications
    ├─ JSON Report
    ├─ Markdown Report
    └─ GitHub PR Comment
```

## Application de démonstration

Une application Next.js simple (Tech News Reader) avec des mauvaises pratiques volontaires :
- Secrets hardcodés dans le code
- Dockerfile non optimisé
- Terraform avec IAM trop permissif
- Security Groups ouverts à 0.0.0.0/0
- Pas d'encryption, pas de tags

## Ce que le pipeline détecte

### Terraform
- Politiques IAM avec wildcards (Action: "*", Resource: "*")
- Security Groups ouverts à Internet (0.0.0.0/0)
- Ressources sans encryption KMS
- Secrets hardcodés
- Absence de tags
- Pas de logging CloudWatch

### Dockerfile
- Images sans version (latest)
- Exécution en tant que root
- Secrets dans les variables d'environnement
- Pas de multi-stage build
- Pas de HEALTHCHECK

### Code applicatif
- API keys hardcodées
- console.log en production
- Pas de validation des données
- Gestion d'erreurs insuffisante

## Installation locale

```bash
# Cloner le repo
git clone https://github.com/MerkeyDiav/smart-devops-pipeline.git
cd smart-devops-pipeline

# Installer les dépendances Python
pip install -r pipeline/requirements.txt

# Configurer AWS
aws configure

# Tester le pipeline
python pipeline/main.py
```

## Utilisation

Le pipeline s'exécute automatiquement sur chaque push et Pull Request. Il génère :
- `pipeline_report.json` : rapport complet
- `pipeline_report.md` : rapport lisible
- `pipeline_blocked.txt` : créé si le déploiement est bloqué
- Commentaire automatique dans les PR GitHub

## Décisions du Gatekeeper

- **BLOCK** : Au moins 1 issue critique → Déploiement bloqué
- **WARN** : Plus de 3 issues high ou 10 medium → Avertissement
- **PASS** : Aucune issue critique → Déploiement approuvé

## Technologies

- **Application** : Next.js 14, React 18, TypeScript
- **Infrastructure** : Terraform, AWS ECS Fargate, ECR, ALB
- **Pipeline** : Python, GitHub Actions
- **IA** : Amazon Bedrock (Nova Pro)
- **Scanners** : Trivy, TFLint, Checkov

## Coûts AWS

- Amazon Bedrock Nova Pro : ~$0.003 par 1K tokens
- Coût estimé par exécution : $0.05 - $0.20
- Gratuit dans le Free Tier Bedrock


## Auteur

Nehemie Nzuzi
