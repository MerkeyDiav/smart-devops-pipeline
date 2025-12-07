#!/usr/bin/env python3
"""
Bedrock Client - Interface pour Amazon Bedrock
"""

import json
import boto3
from typing import Dict, Any


class BedrockClient:
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
    
    def invoke(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> Dict[str, Any]:
        """Invoke Bedrock model avec un prompt"""
        try:
            # Déterminer le format selon le modèle
            if "anthropic" in self.model_id:
                # Format Claude
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            elif "amazon.titan" in self.model_id:
                # Format Amazon Titan
                body = json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                })
            elif "amazon.nova" in self.model_id:
                # Format Amazon Nova (utilise Converse API)
                body = json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                })
            else:
                # Format générique
                body = json.dumps({
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extraire le contenu selon le modèle
            if "anthropic" in self.model_id:
                content = response_body['content'][0]['text']
            elif "amazon.titan" in self.model_id:
                content = response_body['results'][0]['outputText']
            elif "amazon.nova" in self.model_id:
                content = response_body['output']['message']['content'][0]['text']
            else:
                content = str(response_body)
            
            return {
                "success": True,
                "content": content,
                "model": self.model_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_json(self, content: str) -> Dict[str, Any]:
        """Extrait le JSON de la réponse de l'IA"""
        try:
            # Chercher le JSON dans la réponse
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "error": "No JSON found in response",
                    "raw_content": content
                }
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON decode error: {str(e)}",
                "raw_content": content
            }


def main():
    """Test du client Bedrock"""
    client = BedrockClient(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
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

Format JSON:
{
  "issues": [
    {
      "severity": "critical",
      "title": "titre",
      "description": "description"
    }
  ]
}
"""
    
    print("Testing Bedrock Client...\n")
    result = client.invoke(test_prompt)
    
    if result["success"]:
        print("Response received:")
        print(result["content"][:500])
        
        print("\nExtracting JSON...")
        json_data = client.extract_json(result["content"])
        print(json.dumps(json_data, indent=2))
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
