#!/usr/bin/env python3
"""
TFLint Scanner - Scan Terraform pour erreurs de syntaxe et best practices
"""

import subprocess
import json
import os
from typing import Dict, List, Any
from pathlib import Path


class TFLintScanner:
    def __init__(self):
        self.results = []
    
    def scan_terraform(self, terraform_dir: str = "terraform") -> Dict[str, Any]:
        """Scan les fichiers Terraform avec TFLint"""
        if not os.path.exists(terraform_dir):
            return {"error": f"Terraform directory not found: {terraform_dir}"}
        
        try:
            # Init TFLint
            subprocess.run(
                ["tflint", "--init"],
                cwd=terraform_dir,
                capture_output=True
            )
            
            # Scan avec TFLint
            cmd = [
                "tflint",
                "--format", "json",
                "--force"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_tflint_results(data, terraform_dir)
            else:
                return {
                    "scanner": "tflint",
                    "source": terraform_dir,
                    "issues": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0}
                }
            
        except FileNotFoundError:
            return {
                "error": "TFLint not installed",
                "message": "Install with: brew install tflint or curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_tflint_results(self, data: Dict, source: str) -> Dict[str, Any]:
        """Parse les résultats TFLint en format standardisé"""
        issues = []
        
        if "issues" in data:
            for issue in data["issues"]:
                severity = self._map_severity(issue.get("rule", {}).get("severity", "warning"))
                
                issues.append({
                    "type": "terraform_lint",
                    "severity": severity,
                    "title": issue.get("rule", {}).get("name", "Unknown rule"),
                    "description": issue.get("message", ""),
                    "file": issue.get("range", {}).get("filename", ""),
                    "line": issue.get("range", {}).get("start", {}).get("line", 0),
                    "rule": issue.get("rule", {}).get("link", ""),
                    "confidence": 1.0
                })
        
        return {
            "scanner": "tflint",
            "source": source,
            "issues": issues,
            "summary": {
                "total": len(issues),
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"])
            }
        }
    
    def _map_severity(self, tflint_severity: str) -> str:
        """Map TFLint severity to standard severity"""
        mapping = {
            "error": "high",
            "warning": "medium",
            "notice": "low"
        }
        return mapping.get(tflint_severity.lower(), "medium")


def main():
    """Test du scanner"""
    scanner = TFLintScanner()
    
    print("TFLint Scanner - Test\n")
    
    if os.path.exists("terraform"):
        print("Scanning Terraform files...")
        result = scanner.scan_terraform()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
