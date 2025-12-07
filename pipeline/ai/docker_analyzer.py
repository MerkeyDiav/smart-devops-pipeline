#!/usr/bin/env python3
"""
Docker Analyzer - Analyse Dockerfile avec IA
"""

import os
from typing import Dict, Any
from .bedrock_client import BedrockClient


class DockerAnalyzer:
    def __init__(self, bedrock_client: BedrockClient):
        self.client = bedrock_client
    
    def analyze_dockerfile(self, dockerfile_path: str = "Dockerfile") -> Dict[str, Any]:
        """Analyse un Dockerfile avec l'IA"""
        if not os.path.exists(dockerfile_path):
            return {"error": f"Dockerfile not found: {dockerfile_path}"}
        
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt = self._build_prompt(dockerfile_path, content)
            response = self.client.invoke(prompt)
            
            if not response["success"]:
                return {"error": response["error"]}
            
            json_data = self.client.extract_json(response["content"])
            
            if "error" in json_data:
                return json_data
            
            # Ajouter metadata
            if "issues" in json_data:
                for issue in json_data["issues"]:
                    issue["file"] = dockerfile_path
                    issue["type"] = "ai_docker"
            
            return {
                "scanner": "ai_docker",
                "source": dockerfile_path,
                "issues": json_data.get("issues", []),
                "summary": {
                    "total": len(json_data.get("issues", [])),
                    "critical": len([i for i in json_data.get("issues", []) if i["severity"] == "critical"]),
                    "high": len([i for i in json_data.get("issues", []) if i["severity"] == "high"]),
                    "medium": len([i for i in json_data.get("issues", []) if i["severity"] == "medium"])
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _build_prompt(self, file_path: str, content: str) -> str:
        """Construit le prompt pour l'analyse Docker"""
        return f"""Tu es un expert Docker et sécurité des containers. Analyse ce Dockerfile et détecte TOUTES les mauvaises pratiques.

Fichier: {file_path}

```dockerfile
{content}
```

Identifie:
1. Images sans version spécifique (latest, non-pinned)
2. Absence de multi-stage build
3. Exécution en tant que root (pas de USER)
4. Secrets dans l'image (ENV avec passwords, keys, tokens)
5. Packages inutiles ou vulnérables
6. Absence de HEALTHCHECK
7. Trop de layers (optimisation)
8. Variables d'environnement sensibles en clair
9. COPY . . sans .dockerignore
10. npm install au lieu de npm ci
11. Pas de version pinning pour les dépendances

Réponds UNIQUEMENT en JSON avec cette structure exacte:
{{
  "file": "{file_path}",
  "issues": [
    {{
      "line": <numéro de ligne>,
      "severity": "critical|high|medium|low",
      "title": "Titre court",
      "description": "Description détaillée",
      "recommendation": "Comment corriger avec exemple",
      "confidence": 0.0-1.0
    }}
  ]
}}

Sois strict et détecte TOUS les problèmes."""
        
        return prompt


def main():
    """Test de l'analyzer"""
    import json
    
    client = BedrockClient(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    )
    
    analyzer = DockerAnalyzer(client)
    
    print("Docker Analyzer - Test\n")
    
    if os.path.exists("Dockerfile"):
        print("Analyzing Dockerfile...")
        result = analyzer.analyze_dockerfile()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
