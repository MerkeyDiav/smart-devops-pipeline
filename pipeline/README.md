# Smart DevOps Pipeline



## Architecture

```
Phase 1: Scanners Classiques
├─ Trivy (Docker + secrets)
├─ TFLint (Terraform syntax)
└─ Checkov (IaC security)

Phase 2: AI Review (Amazon Bedrock)
├─ Terraform Analyzer
├─ Dockerfile Analyzer
└─ Code Analyzer

Phase 3: Gatekeeper
└─ Decision: BLOCK / WARN / PASS

Phase 4: Reporting
├─ JSON Report
└─ Markdown Report
```

## Installation

### 1. Installer les scanners

```bash
# Trivy
brew install trivy
# ou
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# TFLint
brew install tflint
# ou
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Checkov
pip install checkov
```

### 2. Installer les dépendances Python

```bash
cd pipeline
pip install -r requirements.txt
```

### 3. Configurer AWS

```bash
aws configure
# Entrer vos credentials AWS
# Vérifier l'accès à Bedrock dans us-east-1
```

## Configuration

Éditer `pipeline/config.json` :

```json
{
  "bedrock": {
    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "region": "us-east-1"
  },
  "thresholds": {
    "critical": 0,    // 0 critical = BLOCK
    "high": 3,        // >3 high = WARN
    "medium": 10      // >10 medium = WARN
  },
  "scanners": {
    "trivy": true,
    "tflint": true,
    "checkov": true,
    "ai_review": true
  }
}
```

## Utilisation

### Exécution locale

```bash
# Depuis la racine du projet
python pipeline/main.py
```

### Test des composants individuels

```bash
# Test Trivy
python pipeline/scanners/trivy_scanner.py

# Test TFLint
python pipeline/scanners/tflint_scanner.py

# Test Checkov
python pipeline/scanners/checkov_scanner.py

# Test AI Terraform Analyzer
python pipeline/ai/terraform_analyzer.py

# Test AI Docker Analyzer
python pipeline/ai/docker_analyzer.py

# Test AI Code Analyzer
python pipeline/ai/code_analyzer.py
```

## Résultats

Le pipeline génère :

1. **pipeline_report.json** - Rapport complet en JSON
2. **pipeline_report.md** - Rapport lisible en Markdown
3. **pipeline_blocked.txt** - Créé si le déploiement est bloqué

## Décisions

### BLOCK
- Au moins 1 issue critique détectée
- Le pipeline retourne exit code 1
- Le déploiement est bloqué

### WARN
- Plus de 3 issues high OU plus de 10 issues medium
- Le pipeline retourne exit code 0
- Le déploiement continue avec avertissement

### PASS
- Aucune issue critique ou high
- Le pipeline retourne exit code 0
- Le déploiement est approuvé

## Intégration GitHub Actions

Créer `.github/workflows/smart-pipeline.yml` :

```yaml
name: Smart DevOps Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install scanners
        run: |
          # Trivy
          wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
          echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
          sudo apt-get update
          sudo apt-get install trivy
          
          # TFLint
          curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
          
          # Checkov
          pip install checkov
      
      - name: Install Python dependencies
        run: |
          pip install -r pipeline/requirements.txt
      
      - name: Run Smart Pipeline
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-east-1
        run: |
          python pipeline/main.py
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-reports
          path: |
            pipeline_report.json
            pipeline_report.md
```

## Exemples de détection

### Terraform
- IAM policies avec wildcards
- Security Groups ouverts à 0.0.0.0/0
- Ressources sans encryption
- Secrets hardcodés
- Absence de tags

### Dockerfile
- Images sans version (latest)
- Exécution en root
- Secrets dans ENV
- Pas de multi-stage build
- Pas de HEALTHCHECK

### Code
- API keys hardcodées
- console.log en production
- Pas de validation des données
- Gestion d'erreurs insuffisante

## Coûts AWS

- Amazon Bedrock (Claude 3.5 Sonnet) : ~$0.003 par 1K tokens
- Coût estimé par exécution : $0.05 - $0.20
- Gratuit si vous êtes dans le Free Tier Bedrock

## Troubleshooting

### Erreur "Bedrock not available"
```bash
# Vérifier l'accès à Bedrock
aws bedrock list-foundation-models --region us-east-1

# Activer Bedrock dans la console AWS si nécessaire
```

### Erreur "Scanner not found"
```bash
# Vérifier l'installation
trivy --version
tflint --version
checkov --version
```

### Erreur "No issues found"
C'est normal si votre code est parfait ! Testez avec les fichiers d'exemple qui contiennent des mauvaises pratiques volontaires.
