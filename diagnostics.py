import asyncio
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

# Add the current directory to path so we can import the model
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import utility functions first
from async_utils import get_or_create_eventloop, setup_asyncio_patch, diagnose_asyncio_environment
from model import DisasterImpactModel

async def test_api_directly():
    """Test the API connection directly without going through the model class"""
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCZgOxF-3zDgw-Xtr0AcN-pD3GSRVAFdHI')
    
    print(f"Testing API with key: {api_key[:5]}...{api_key[-5:]}")
    
    genai.configure(api_key=api_key)
    
    models = [
        "gemini-pro",
        "gemini-1.5-pro",
        "models/gemini-pro-latest"
    ]
    
    for model_name in models:
        try:
            print(f"\nTrying model {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            print("Sending test query...")
            response = await model.generate_content_async("Hello, respond with one word only")
            
            print(f"Response received: {response.text}")
            print(f"✓ Success with model: {model_name}")
            
            # Try a more complex query
            print("\nTrying disaster impact query...")
            prompt = """Generate disaster impact data for coordinates (21.19, 82.73).
            Output numbers only in this format:
            Total Population: [number]
            Economic Loss (INR): [number]
            Houses Damaged: [number]"""
            
            response = await model.generate_content_async(prompt)
            print(f"Response received: {response.text[:100]}...")
            break
            
        except Exception as e:
            print(f"✗ Failed with model {model_name}: {str(e)}")

async def test_through_model():
    """Test the API connection through the model class"""
    print("\nTesting through DisasterImpactModel class...")
    model = DisasterImpactModel()
    
    if model.api_client:
        print(f"Model initialized with: {model.current_model_name}")
        
        # Test connection
        print("Testing connection...")
        connected = await model.test_api_connection()
        print(f"Connection test: {'Success' if connected else 'Failed'}")
        
        # Test data retrieval
        if connected:
            print("\nTesting data retrieval...")
            data = await model.get_data_from_api(21.19, 82.73)
            
            if data:
                print("✓ Successfully retrieved data")
                print("\nSample data:")
                for key, value in list(data.items())[:5]:
                    print(f"- {key}: {value}")
            else:
                print("✗ Failed to retrieve data")
    else:
        print("✗ Failed to initialize API client")

async def run_diagnostics():
    """Run all diagnostic tests"""
    print("=== API DIAGNOSTICS ===")
    
    # Run diagnostics first
    diagnose_asyncio_environment()
    
    # Apply nest_asyncio patch
    setup_asyncio_patch()
    
    print("\nTesting API directly...")
    await test_api_directly()
    
    print("\n" + "=" * 50)
    
    print("\nTesting through model...")
    await test_through_model()
    
    print("\n=== DIAGNOSTICS COMPLETE ===")

if __name__ == "__main__":
    # Get or create event loop
    loop = get_or_create_eventloop()
    
    # Run the diagnostics
    loop.run_until_complete(run_diagnostics())
    
    print("\nTo run diagnostics from command line:")
    print("python diagnostics.py")
