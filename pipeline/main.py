#!/usr/bin/env python3
"""
Smart DevOps Pipeline - Orchestrateur principal
"""

import json
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from scanners.trivy_scanner import TrivyScanner
from scanners.tflint_scanner import TFLintScanner
from scanners.checkov_scanner import CheckovScanner
from ai.bedrock_client import BedrockClient
from ai.terraform_analyzer import TerraformAnalyzer
from ai.docker_analyzer import DockerAnalyzer
from ai.code_analyzer import CodeAnalyzer
from gatekeeper import Gatekeeper
from reporter import Reporter


class SmartPipeline:
    def __init__(self, config_path: str = "pipeline/config.json"):
        # Charger la configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialiser les composants
        self.trivy = TrivyScanner()
        self.tflint = TFLintScanner()
        self.checkov = CheckovScanner()
        
        # Bedrock client
        bedrock_config = self.config["bedrock"]
        self.bedrock_client = BedrockClient(
            model_id=bedrock_config["model_id"],
            region=bedrock_config["region"]
        )
        
        # AI Analyzers
        self.terraform_analyzer = TerraformAnalyzer(self.bedrock_client)
        self.docker_analyzer = DockerAnalyzer(self.bedrock_client)
        self.code_analyzer = CodeAnalyzer(self.bedrock_client)
        
        # Gatekeeper et Reporter
        self.gatekeeper = Gatekeeper(self.config)
        self.reporter = Reporter()
        
        self.results = []
    
    def run(self):
        """Exécute le pipeline complet"""
        print("=" * 60)
        print("SMART DEVOPS PIPELINE - AI-POWERED SECURITY ANALYSIS")
        print("=" * 60)
        print()
        
        # Phase 1: Scanners classiques
        print("[PHASE 1] Running Classic Scanners...")
        print("-" * 60)
        
        if self.config["scanners"]["trivy"]:
            print("\n[1/3] Trivy Scanner...")
            trivy_result = self.trivy.scan_dockerfile()
            if "error" not in trivy_result:
                self.results.append(trivy_result)
                print(f"  Found {trivy_result['summary']['total']} issues")
            else:
                print(f"  Warning: {trivy_result.get('error', 'Unknown error')}")
        
        if self.config["scanners"]["tflint"]:
            print("\n[2/3] TFLint Scanner...")
            tflint_result = self.tflint.scan_terraform()
            if "error" not in tflint_result:
                self.results.append(tflint_result)
                print(f"  Found {tflint_result['summary']['total']} issues")
            else:
                print(f"  Warning: {tflint_result.get('error', 'Unknown error')}")
        
        if self.config["scanners"]["checkov"]:
            print("\n[3/3] Checkov Scanner...")
            checkov_result = self.checkov.scan_iac()
            if "error" not in checkov_result:
                self.results.append(checkov_result)
                print(f"  Found {checkov_result['summary']['total']} issues")
            else:
                print(f"  Warning: {checkov_result.get('error', 'Unknown error')}")
        
        # Phase 2: AI Review
        if self.config["scanners"]["ai_review"]:
            print("\n\n[PHASE 2] AI-Powered Analysis (Amazon Bedrock)...")
            print("-" * 60)
            
            print("\n[1/3] Analyzing Terraform with AI...")
            terraform_result = self.terraform_analyzer.analyze_directory("terraform")
            if "error" not in terraform_result:
                self.results.append(terraform_result)
                print(f"  Found {terraform_result['summary']['total']} issues")
            else:
                print(f"  Error: {terraform_result.get('error', 'Unknown error')}")
            
            print("\n[2/3] Analyzing Dockerfile with AI...")
            docker_result = self.docker_analyzer.analyze_dockerfile()
            if "error" not in docker_result:
                self.results.append(docker_result)
                print(f"  Found {docker_result['summary']['total']} issues")
            else:
                print(f"  Error: {docker_result.get('error', 'Unknown error')}")
            
            print("\n[3/3] Analyzing Code with AI...")
            code_result = self.code_analyzer.analyze_directory("app")
            if "error" not in code_result:
                self.results.append(code_result)
                print(f"  Found {code_result['summary']['total']} issues")
            else:
                print(f"  Error: {code_result.get('error', 'Unknown error')}")
        
        # Phase 3: Gatekeeper Decision
        print("\n\n[PHASE 3] Gatekeeper Decision...")
        print("-" * 60)
        
        gatekeeper_result = self.gatekeeper.evaluate(self.results)
        
        print(f"\nDecision: {gatekeeper_result['decision']}")
        print(f"Risk Score: {gatekeeper_result['risk_score']}/100")
        print(f"Total Issues: {gatekeeper_result['total_issues']}")
        print(f"\nSeverity Breakdown:")
        print(f"  Critical: {gatekeeper_result['severity_counts']['critical']}")
        print(f"  High:     {gatekeeper_result['severity_counts']['high']}")
        print(f"  Medium:   {gatekeeper_result['severity_counts']['medium']}")
        print(f"  Low:      {gatekeeper_result['severity_counts']['low']}")
        print(f"\nMessage: {gatekeeper_result['message']}")
        
        # Phase 4: Reporting
        print("\n\n[PHASE 4] Generating Reports...")
        print("-" * 60)
        
        json_report = self.reporter.generate_json_report(gatekeeper_result)
        print(f"\nJSON Report: {json_report}")
        
        if self.config["reporting"]["generate_markdown"]:
            md_report = self.reporter.generate_markdown_report(gatekeeper_result)
            print(f"Markdown Report: {md_report}")
        
        # Créer un fichier marker si BLOCK
        if gatekeeper_result["decision"] == "BLOCK":
            with open("pipeline_blocked.txt", "w") as f:
                f.write(gatekeeper_result["message"])
            print("\nPipeline BLOCKED - See pipeline_blocked.txt")
        
        print("\n" + "=" * 60)
        print("PIPELINE EXECUTION COMPLETED")
        print("=" * 60)
        
        # Exit code basé sur la décision
        if gatekeeper_result["decision"] == "BLOCK":
            sys.exit(1)
        elif gatekeeper_result["decision"] == "WARN":
            sys.exit(0)  # Warning mais on laisse passer
        else:
            sys.exit(0)


def main():
    """Point d'entrée principal"""
    try:
        pipeline = SmartPipeline()
        pipeline.run()
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
