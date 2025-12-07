#!/usr/bin/env python3
"""
Checkov Scanner - Scan IaC pour problèmes de sécurité et compliance
"""

import subprocess
import json
import os
from typing import Dict, List, Any


class CheckovScanner:
    def __init__(self):
        self.results = []
    
    def scan_iac(self, directory: str = ".") -> Dict[str, Any]:
        """Scan Infrastructure as Code avec Checkov"""
        try:
            cmd = [
                "checkov",
                "--directory", directory,
                "--output", "json",
                "--quiet",
                "--compact",
                "--framework", "terraform,dockerfile"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Checkov retourne exit code 1 si des issues sont trouvées
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_checkov_results(data, directory)
            else:
                return {
                    "scanner": "checkov",
                    "source": directory,
                    "issues": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0}
                }
            
        except FileNotFoundError:
            return {
                "error": "Checkov not installed",
                "message": "Install with: pip install checkov"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_checkov_results(self, data: Dict, source: str) -> Dict[str, Any]:
        """Parse les résultats Checkov en format standardisé"""
        issues = []
        
        # Checkov retourne les résultats par type de check
        if "results" in data:
            results = data["results"]
            
            # Failed checks
            if "failed_checks" in results:
                for check in results["failed_checks"]:
                    severity = self._map_severity(check.get("check_class", ""))
                    
                    issues.append({
                        "type": "iac_security",
                        "severity": severity,
                        "title": check.get("check_name", "Unknown check"),
                        "description": check.get("check_result", {}).get("result", ""),
                        "file": check.get("file_path", ""),
                        "line": check.get("file_line_range", [0])[0] if check.get("file_line_range") else 0,
                        "check_id": check.get("check_id", ""),
                        "guideline": check.get("guideline", ""),
                        "recommendation": check.get("fixed_definition", ""),
                        "confidence": 0.95
                    })
        
        return {
            "scanner": "checkov",
            "source": source,
            "issues": issues,
            "summary": {
                "total": len(issues),
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"])
            }
        }
    
    def _map_severity(self, check_class: str) -> str:
        """Map Checkov check class to severity"""
        # Checkov n'a pas de severity explicite, on infère par le type
        critical_keywords = ["secret", "credential", "password", "key", "token"]
        high_keywords = ["encryption", "public", "open", "wildcard", "admin"]
        
        check_lower = check_class.lower()
        
        if any(keyword in check_lower for keyword in critical_keywords):
            return "critical"
        elif any(keyword in check_lower for keyword in high_keywords):
            return "high"
        else:
            return "medium"


def main():
    """Test du scanner"""
    scanner = CheckovScanner()
    
    print("Checkov Scanner - Test\n")
    
    print("Scanning Infrastructure as Code...")
    result = scanner.scan_iac(".")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
