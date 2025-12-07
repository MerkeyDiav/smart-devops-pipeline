#!/usr/bin/env python3
"""
Trivy Scanner - Scan Docker images et fichiers pour les vulnérabilités
"""

import subprocess
import json
import os
from typing import Dict, List, Any


class TrivyScanner:
    def __init__(self):
        self.results = []
    
    def scan_dockerfile(self, dockerfile_path: str = "Dockerfile") -> Dict[str, Any]:
        """Scan un Dockerfile avec Trivy"""
        if not os.path.exists(dockerfile_path):
            return {"error": f"Dockerfile not found: {dockerfile_path}"}
        
        try:
            # Scan du Dockerfile en mode config
            cmd = [
                "trivy",
                "config",
                "--format", "json",
                "--severity", "CRITICAL,HIGH,MEDIUM",
                dockerfile_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "error": "Trivy scan failed",
                    "stderr": result.stderr
                }
            
            data = json.loads(result.stdout)
            return self._parse_trivy_results(data, dockerfile_path)
            
        except FileNotFoundError:
            return {
                "error": "Trivy not installed",
                "message": "Install with: brew install trivy or apt-get install trivy"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def scan_filesystem(self, path: str = ".") -> Dict[str, Any]:
        """Scan le filesystem pour secrets et vulnérabilités"""
        try:
            cmd = [
                "trivy",
                "fs",
                "--format", "json",
                "--severity", "CRITICAL,HIGH,MEDIUM",
                "--scanners", "vuln,secret,config",
                path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "error": "Trivy filesystem scan failed",
                    "stderr": result.stderr
                }
            
            data = json.loads(result.stdout)
            return self._parse_trivy_results(data, path)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_trivy_results(self, data: Dict, source: str) -> Dict[str, Any]:
        """Parse les résultats Trivy en format standardisé"""
        issues = []
        
        if "Results" in data:
            for result in data["Results"]:
                target = result.get("Target", source)
                
                # Vulnérabilités
                if "Vulnerabilities" in result and result["Vulnerabilities"]:
                    for vuln in result["Vulnerabilities"]:
                        issues.append({
                            "type": "vulnerability",
                            "severity": vuln.get("Severity", "UNKNOWN").lower(),
                            "title": vuln.get("VulnerabilityID", "Unknown"),
                            "description": vuln.get("Title", "No description"),
                            "package": vuln.get("PkgName", ""),
                            "installed_version": vuln.get("InstalledVersion", ""),
                            "fixed_version": vuln.get("FixedVersion", ""),
                            "file": target,
                            "confidence": 1.0
                        })
                
                # Secrets
                if "Secrets" in result and result["Secrets"]:
                    for secret in result["Secrets"]:
                        issues.append({
                            "type": "secret",
                            "severity": "critical",
                            "title": secret.get("Title", "Secret detected"),
                            "description": secret.get("Match", ""),
                            "file": target,
                            "line": secret.get("StartLine", 0),
                            "confidence": 0.9
                        })
                
                # Misconfigurations
                if "Misconfigurations" in result and result["Misconfigurations"]:
                    for misconfig in result["Misconfigurations"]:
                        issues.append({
                            "type": "misconfiguration",
                            "severity": misconfig.get("Severity", "UNKNOWN").lower(),
                            "title": misconfig.get("Title", "Misconfiguration"),
                            "description": misconfig.get("Description", ""),
                            "file": target,
                            "line": misconfig.get("CauseMetadata", {}).get("StartLine", 0),
                            "recommendation": misconfig.get("Resolution", ""),
                            "confidence": 0.95
                        })
        
        return {
            "scanner": "trivy",
            "source": source,
            "issues": issues,
            "summary": {
                "total": len(issues),
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"])
            }
        }


def main():
    """Test du scanner"""
    scanner = TrivyScanner()
    
    print("Trivy Scanner - Test\n")
    
    # Scan Dockerfile
    if os.path.exists("Dockerfile"):
        print("Scanning Dockerfile...")
        result = scanner.scan_dockerfile()
        print(json.dumps(result, indent=2))
    
    # Scan filesystem
    print("\nScanning filesystem...")
    result = scanner.scan_filesystem(".")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
