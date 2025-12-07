#!/usr/bin/env python3
"""
Gatekeeper - Décision finale basée sur les résultats des scans
"""

import json
from typing import Dict, List, Any


class Gatekeeper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get("thresholds", {
            "critical": 0,
            "high": 3,
            "medium": 10
        })
    
    def evaluate(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Évalue tous les résultats et prend une décision"""
        
        # Agréger tous les issues
        all_issues = []
        for result in all_results:
            if "issues" in result:
                all_issues.extend(result["issues"])
        
        # Filtrer par confidence threshold
        confidence_threshold = self.config.get("false_positives", {}).get("confidence_threshold", 0.7)
        filtered_issues = [
            issue for issue in all_issues
            if issue.get("confidence", 1.0) >= confidence_threshold
        ]
        
        # Compter par severity
        severity_counts = {
            "critical": len([i for i in filtered_issues if i.get("severity") == "critical"]),
            "high": len([i for i in filtered_issues if i.get("severity") == "high"]),
            "medium": len([i for i in filtered_issues if i.get("severity") == "medium"]),
            "low": len([i for i in filtered_issues if i.get("severity") == "low"])
        }
        
        # Calculer le risk score (0-100)
        risk_score = self._calculate_risk_score(severity_counts)
        
        # Décision
        decision = self._make_decision(severity_counts)
        
        # Grouper les issues par fichier
        issues_by_file = {}
        for issue in filtered_issues:
            file_path = issue.get("file", "unknown")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        return {
            "decision": decision,
            "risk_score": risk_score,
            "severity_counts": severity_counts,
            "total_issues": len(filtered_issues),
            "issues_by_file": issues_by_file,
            "all_issues": filtered_issues,
            "thresholds": self.thresholds,
            "message": self._get_decision_message(decision, severity_counts)
        }
    
    def _calculate_risk_score(self, severity_counts: Dict[str, int]) -> int:
        """Calcule un score de risque de 0 à 100"""
        score = 0
        score += severity_counts.get("critical", 0) * 25
        score += severity_counts.get("high", 0) * 10
        score += severity_counts.get("medium", 0) * 3
        score += severity_counts.get("low", 0) * 1
        
        return min(score, 100)
    
    def _make_decision(self, severity_counts: Dict[str, int]) -> str:
        """Prend la décision finale: BLOCK, WARN, ou PASS"""
        
        if severity_counts.get("critical", 0) > self.thresholds.get("critical", 0):
            return "BLOCK"
        
        if severity_counts.get("high", 0) > self.thresholds.get("high", 3):
            return "WARN"
        
        if severity_counts.get("medium", 0) > self.thresholds.get("medium", 10):
            return "WARN"
        
        return "PASS"
    
    def _get_decision_message(self, decision: str, severity_counts: Dict[str, int]) -> str:
        """Génère un message explicatif"""
        if decision == "BLOCK":
            return f"Deployment BLOCKED: {severity_counts.get('critical', 0)} critical issue(s) found. Fix them before deploying."
        
        elif decision == "WARN":
            return f"Deployment allowed with WARNINGS: {severity_counts.get('high', 0)} high and {severity_counts.get('medium', 0)} medium issues found. Review recommended."
        
        else:
            return "Deployment APPROVED: No critical issues found."


def main():
    """Test du gatekeeper"""
    
    # Simuler des résultats
    mock_results = [
        {
            "scanner": "trivy",
            "issues": [
                {"severity": "critical", "title": "Secret detected", "confidence": 1.0, "file": "Dockerfile"},
                {"severity": "high", "title": "Vulnerability", "confidence": 0.9, "file": "package.json"}
            ]
        },
        {
            "scanner": "ai_terraform",
            "issues": [
                {"severity": "critical", "title": "IAM wildcard", "confidence": 0.95, "file": "terraform/iam.tf"},
                {"severity": "high", "title": "SG open to world", "confidence": 1.0, "file": "terraform/networking.tf"}
            ]
        }
    ]
    
    config = {
        "thresholds": {
            "critical": 0,
            "high": 3,
            "medium": 10
        },
        "false_positives": {
            "confidence_threshold": 0.7
        }
    }
    
    gatekeeper = Gatekeeper(config)
    result = gatekeeper.evaluate(mock_results)
    
    print("Gatekeeper Decision:\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
