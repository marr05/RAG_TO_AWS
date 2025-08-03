import boto3
import json

def check_bedrock_models():
    """Check which Bedrock models are available in your account"""
    
    # Try different regions if needed
    regions_to_check = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    for region in regions_to_check:
        print(f"\n{'='*50}")
        print(f"Checking region: {region}")
        print('='*50)
        
        try:
            # Create Bedrock client
            bedrock = boto3.client('bedrock', region_name=region)
            
            # List all foundation models
            response = bedrock.list_foundation_models()
            
            # Filter for embedding models
            embedding_models = []
            for model in response['modelSummaries']:
                if 'embed' in model['modelId'].lower():
                    embedding_models.append(model)
            
            if embedding_models:
                print(f"\nFound {len(embedding_models)} embedding models in {region}:")
                for model in embedding_models:
                    print(f"\nModel ID: {model['modelId']}")
                    print(f"Model Name: {model['modelName']}")
                    print(f"Provider: {model['providerName']}")
                    if 'responseStreamingSupported' in model:
                        print(f"Streaming: {model['responseStreamingSupported']}")
                        
                # Check model access
                print(f"\n{'='*30}")
                print("Checking model access status...")
                print('='*30)
                
                # Try to get model access details
                try:
                    # This requires different permissions, so it might fail
                    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
                    
                    # Test with Titan Embeddings
                    test_model_id = "amazon.titan-embed-text-v1"
                    print(f"\nTesting access to {test_model_id}...")
                    
                    try:
                        # Try to invoke the model with a test text
                        test_body = json.dumps({
                            "inputText": "test"
                        })
                        
                        response = bedrock_runtime.invoke_model(
                            modelId=test_model_id,
                            contentType="application/json",
                            accept="application/json",
                            body=test_body
                        )
                        print(f"✅ Successfully accessed {test_model_id}")
                    except Exception as e:
                        print(f"❌ Cannot access {test_model_id}: {str(e)}")
                        
                except Exception as e:
                    print(f"\nNote: Could not check runtime access: {str(e)}")
                    print("You may need to enable model access in the AWS Console")
                    
            else:
                print(f"\nNo embedding models found in {region}")
                
        except Exception as e:
            print(f"\nError accessing Bedrock in {region}: {str(e)}")
    
    print(f"\n{'='*50}")
    print("NEXT STEPS:")
    print("1. Go to AWS Console → Amazon Bedrock → Model access")
    print("2. Click 'Manage model access'")
    print("3. Enable the embedding models you want to use")
    print("4. Wait a few minutes for the models to be provisioned")
    print('='*50)

if __name__ == "__main__":
    check_bedrock_models()