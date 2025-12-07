#!/usr/bin/env python3
"""
Script de test simple pour le pipeline
"""

import sys
import os

# Ajouter le répertoire pipeline au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

from ai.bedrock_client import BedrockClient
from ai.terraform_analyzer import TerraformAnalyzer
import json


def test_bedrock_connection():
    """Test de connexion à Bedrock"""
    print("=" * 60)
    print("TEST 1: Bedrock Connection")
    print("=" * 60)
    
    client = BedrockClient(
        model_id="amazon.nova-pro-v1:0",
        region="us-east-1"
    )
    
    test_prompt = """Analyse ce code Terraform et réponds en JSON:

resource "aws_security_group" "test" {
  ingress {
    from_port = 0
    to_port = 65535
    cidr_blocks = ["0.0.0.0/0"]
  }
}

Réponds UNIQUEMENT en JSON:
{
  "issues": [
    {
      "severity": "critical",
      "title": "Security Group ouvert",
      "description": "Le SG accepte tout le trafic"
    }
  ]
}
"""
    
    result = client.invoke(test_prompt)
    
    if result["success"]:
        print("\nBedrock connection: OK")
        print(f"\nUsing model: {result['model']}")
        print("\nResponse preview:")
        print(result["content"][:300])
        
        json_data = client.extract_json(result["content"])
        print("\nExtracted JSON:")
        print(json.dumps(json_data, indent=2))
        return True
    else:
        print(f"\nBedrock connection: FAILED")
        print(f"Error: {result['error']}")
        return False


def test_terraform_analysis():
    """Test de l'analyse Terraform"""
    print("\n\n" + "=" * 60)
    print("TEST 2: Terraform Analysis")
    print("=" * 60)
    
    if not os.path.exists("terraform"):
        print("\nERROR: terraform directory not found")
        return False
    
    client = BedrockClient(
        model_id="amazon.nova-pro-v1:0",
        region="us-east-1"
    )
    
    analyzer = TerraformAnalyzer(client)
    
    print("\nAnalyzing terraform/iam.tf...")
    result = analyzer.analyze_file("terraform/iam.tf")
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False
    
    print(f"\nFound {len(result.get('issues', []))} issues")
    
    if result.get('issues'):
        print("\nTop 3 issues:")
        for issue in result['issues'][:3]:
            print(f"\n- [{issue.get('severity', 'unknown').upper()}] {issue.get('title', 'Unknown')}")
            print(f"  Line: {issue.get('line', 'N/A')}")
            print(f"  Description: {issue.get('description', 'No description')[:100]}...")
    
    return True


def main():
    """Exécute les tests"""
    print("\nSMART DEVOPS PIPELINE - TEST SUITE\n")
    
    # Test 1: Bedrock
    bedrock_ok = test_bedrock_connection()
    
    if not bedrock_ok:
        print("\n\nBedrock test failed. Check your AWS credentials and Bedrock access.")
        sys.exit(1)
    
    # Test 2: Terraform Analysis
    terraform_ok = test_terraform_analysis()
    
    if terraform_ok:
        print("\n\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou can now run the full pipeline:")
        print("  python pipeline/main.py")
    else:
        print("\n\nTerraform analysis test failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
