#!/usr/bin/env python3
"""
Code Analyzer - Analyse le code applicatif avec IA
"""

import os
import glob
from typing import Dict, List, Any
from pathlib import Path
from .bedrock_client import BedrockClient


class CodeAnalyzer:
    def __init__(self, bedrock_client: BedrockClient):
        self.client = bedrock_client
        self.supported_extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go']
    
    def analyze_directory(self, code_dir: str = "app") -> Dict[str, Any]:
        """Analyse les fichiers de code d'un répertoire"""
        if not os.path.exists(code_dir):
            return {"error": f"Directory not found: {code_dir}"}
        
        code_files = []
        for ext in self.supported_extensions:
            code_files.extend(glob.glob(f"{code_dir}/**/*{ext}", recursive=True))
        
        if not code_files:
            return {"error": "No code files found"}
        
        all_issues = []
        
        # Limiter à 5 fichiers pour éviter trop d'appels Bedrock
        for code_file in code_files[:5]:
            result = self.analyze_file(code_file)
            if "issues" in result:
                all_issues.extend(result["issues"])
        
        return {
            "scanner": "ai_code",
            "source": code_dir,
            "files_analyzed": min(len(code_files), 5),
            "issues": all_issues,
            "summary": {
                "total": len(all_issues),
                "critical": len([i for i in all_issues if i["severity"] == "critical"]),
                "high": len([i for i in all_issues if i["severity"] == "high"]),
                "medium": len([i for i in all_issues if i["severity"] == "medium"])
            }
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse un fichier de code avec l'IA"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip si fichier trop gros (>10KB)
            if len(content) > 10000:
                return {"issues": []}
            
            prompt = self._build_prompt(file_path, content)
            response = self.client.invoke(prompt)
            
            if not response["success"]:
                return {"error": response["error"], "file": file_path}
            
            json_data = self.client.extract_json(response["content"])
            
            if "error" in json_data:
                return json_data
            
            # Ajouter metadata
            if "issues" in json_data:
                for issue in json_data["issues"]:
                    issue["file"] = file_path
                    issue["type"] = "ai_code"
            
            return json_data
            
        except Exception as e:
            return {"error": str(e), "file": file_path}
    
    def _build_prompt(self, file_path: str, content: str) -> str:
        """Construit le prompt pour l'analyse de code"""
        file_ext = Path(file_path).suffix
        
        return f"""Tu es un expert en sécurité applicative. Analyse ce code et détecte TOUS les problèmes de sécurité et mauvaises pratiques.

Fichier: {file_path}

```{file_ext[1:]}
{content}
```

Identifie:
1. Secrets hardcodés (API keys, passwords, tokens, credentials)
2. Appels API non sécurisés (HTTP au lieu de HTTPS)
3. Absence de validation des données utilisateur
4. console.log ou print en production
5. Gestion d'erreurs insuffisante (try/catch vides)
6. Données sensibles exposées
7. Injections potentielles (SQL, XSS, Command)
8. Dépendances obsolètes ou vulnérables
9. Authentification/autorisation manquante
10. CORS mal configuré

Réponds UNIQUEMENT en JSON avec cette structure exacte:
{{
  "file": "{file_path}",
  "issues": [
    {{
      "line": <numéro de ligne>,
      "severity": "critical|high|medium|low",
      "title": "Titre court",
      "description": "Description détaillée",
      "recommendation": "Comment corriger avec exemple de code",
      "confidence": 0.0-1.0
    }}
  ]
}}

Sois strict et détecte TOUS les problèmes de sécurité."""
        
        return prompt


def main():
    """Test de l'analyzer"""
    import json
    
    client = BedrockClient(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    )
    
    analyzer = CodeAnalyzer(client)
    
    print("Code Analyzer - Test\n")
    
    if os.path.exists("app"):
        print("Analyzing code directory...")
        result = analyzer.analyze_directory("app")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
