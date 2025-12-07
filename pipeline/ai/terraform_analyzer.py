#!/usr/bin/env python3
"""
Terraform Analyzer - Analyse Terraform avec IA
"""

import os
import glob
from typing import Dict, List, Any
from .bedrock_client import BedrockClient


class TerraformAnalyzer:
    def __init__(self, bedrock_client: BedrockClient):
        self.client = bedrock_client
    
    def analyze_directory(self, terraform_dir: str = "terraform") -> Dict[str, Any]:
        """Analyse tous les fichiers Terraform d'un répertoire"""
        if not os.path.exists(terraform_dir):
            return {"error": f"Directory not found: {terraform_dir}"}
        
        tf_files = glob.glob(f"{terraform_dir}/**/*.tf", recursive=True)
        
        if not tf_files:
            return {"error": "No Terraform files found"}
        
        all_issues = []
        
        for tf_file in tf_files:
            result = self.analyze_file(tf_file)
            if "issues" in result:
                all_issues.extend(result["issues"])
        
        return {
            "scanner": "ai_terraform",
            "source": terraform_dir,
            "files_analyzed": len(tf_files),
            "issues": all_issues,
            "summary": {
                "total": len(all_issues),
                "critical": len([i for i in all_issues if i["severity"] == "critical"]),
                "high": len([i for i in all_issues if i["severity"] == "high"]),
                "medium": len([i for i in all_issues if i["severity"] == "medium"])
            }
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse un fichier Terraform avec l'IA"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            prompt = self._build_prompt(file_path, content)
            response = self.client.invoke(prompt)
            
            if not response["success"]:
                return {"error": response["error"], "file": file_path}
            
            json_data = self.client.extract_json(response["content"])
            
            if "error" in json_data:
                return json_data
            
            # Ajouter le fichier à chaque issue
            if "issues" in json_data:
                for issue in json_data["issues"]:
                    issue["file"] = file_path
                    issue["type"] = "ai_terraform"
            
            return json_data
            
        except Exception as e:
            return {"error": str(e), "file": file_path}
    
    def _build_prompt(self, file_path: str, content: str) -> str:
        """Construit le prompt pour l'analyse Terraform"""
        return f"""Tu es un expert DevOps et sécurité AWS. Analyse ce fichier Terraform et détecte TOUTES les mauvaises pratiques de sécurité et DevOps.

Fichier: {file_path}

```hcl
{content}
```

Identifie:
1. Politiques IAM trop permissives (wildcards *, Action = "*", Resource = "*")
2. Security Groups ouverts (0.0.0.0/0, ports larges)
3. Ressources sans encryption (KMS, AES256)
4. Secrets hardcodés (passwords, keys, tokens)
5. Ressources publiques non nécessaires (publicly_accessible = true)
6. Absence de tags
7. Absence de logging/monitoring (CloudWatch, CloudTrail)
8. Configurations non sécurisées (HTTP au lieu de HTTPS, pas de versioning)
9. Variables sensibles sans sensitive = true
10. Outputs de données sensibles sans sensitive = true

Réponds UNIQUEMENT en JSON avec cette structure exacte:
{{
  "file": "{file_path}",
  "issues": [
    {{
      "line": <numéro de ligne ou 0 si inconnu>,
      "severity": "critical|high|medium|low",
      "title": "Titre court et précis",
      "description": "Description détaillée du problème",
      "recommendation": "Comment corriger avec exemple de code",
      "confidence": 0.0-1.0,
      "resource": "nom de la ressource concernée"
    }}
  ]
}}

Sois strict et détecte TOUS les problèmes, même mineurs."""
        
        return prompt


def main():
    """Test de l'analyzer"""
    import json
    
    client = BedrockClient(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    )
    
    analyzer = TerraformAnalyzer(client)
    
    print("Terraform Analyzer - Test\n")
    
    if os.path.exists("terraform"):
        print("Analyzing Terraform directory...")
        result = analyzer.analyze_directory("terraform")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
