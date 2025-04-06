import pandas as pd
import pickle
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

class DisasterImpactModel:
    def __init__(self):
        self.data = None
        self.model = None
        self.csv_loaded = False
        self.api_client = None
        self.current_model_name = None
        self.init_api_client()

    def init_api_client(self):
        try:
            load_dotenv()
            # Use a hardcoded API key if the .env file doesn't provide one
            api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCZgOxF-3zDgw-Xtr0AcN-pD3GSRVAFdHI')
            
            if api_key:
                print(f"Configuring API with key: {api_key[:5]}...{api_key[-5:]}")
                genai.configure(api_key=api_key)
                
                # Based on diagnostics, prioritize the models that are known to work
                gemini_models = [
                    "gemini-1.5-pro",       # Working in diagnostics
                    "models/gemini-1.5-flash-latest",
                    "models/gemini-1.5-pro-latest",
                    "models/gemini-pro-latest",
                    "gemini-pro"
                ]
                
                successful_model = None
                
                for model_name in gemini_models:
                    try:
                        print(f"Attempting to initialize model: {model_name}")
                        model = genai.GenerativeModel(model_name)
                        
                        # Do a simple synchronous test instead of using event loops
                        print(f"Quick test of {model_name}...")
                        try:
                            # Use the synchronous version to avoid event loop issues
                            response = model.generate_content("Test")
                            
                            if response and hasattr(response, 'text'):
                                # Model works! Save it.
                                self.api_client = model
                                self.current_model_name = model_name
                                print(f"✓ API client initialized and tested with {model_name} successfully")
                                successful_model = model_name
                                break
                            else:
                                print(f"× Model {model_name} returned invalid response")
                        except Exception as e:
                            print(f"× Model {model_name} test failed: {str(e)}")
                    except Exception as e:
                        print(f"× Failed to initialize {model_name}: {str(e)}")
                        continue
                
                if successful_model:
                    print(f"Successfully initialized API with {successful_model}")
                else:
                    print("Failed to initialize any Gemini model")
                    self.api_client = None
                    self.current_model_name = None
            else:
                print("No API key found or provided")
                self.api_client = None
                self.current_model_name = None
        except Exception as e:
            print(f"Error initializing API client: {str(e)}")
            self.api_client = None
            self.current_model_name = None
    
    async def test_api_connection(self):
        """Test if the API connection is working properly"""
        if not self.api_client:
            print("No API client available to test")
            return False
            
        try:
            print(f"Testing API connection with {self.current_model_name}")
            # Send a very simple test query to minimize tokens
            response = await self.api_client.generate_content_async("Hello")
            
            if response and hasattr(response, 'text'):
                print(f"API test successful with {self.current_model_name}, response: {response.text[:20]}...")
                return True
            else:
                print("API response is missing text attribute")
                return False
        except Exception as e:
            print(f"API connection test failed with error: {str(e)}")
            return False

    def load_data(self, csv_path):
        try:
            self.data = pd.read_csv(csv_path)
            self.csv_loaded = True
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            self.csv_loaded = False

    def load_model(self, model_path):
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {str(e)}")

    async def get_data_from_api(self, lat, lon):
        try:
            if not self.api_client:
                print("No API client available")
                return None
                
            # Enhanced prompt for better quality disaster impact data
            prompt = f"""As an AI disaster impact analyzer, provide realistic disaster impact data for coordinates ({lat}, {lon}) in Chhattisgarh, India.
Consider factors like population density, infrastructure quality, and regional vulnerabilities.
Return ONLY numerical values in this format (put only numbers after the colon):
Total Population: [number]
Economic Loss (INR): [number]
Houses Damaged: [number]
Shops Damaged: [number]
Hotels Damaged: [number]
Schools Damaged: [number]
Children (%): [number]
Adults (%): [number]
Elderly (%): [number]
Male (%): [number]
Female (%): [number]
Diabetes Cases: [number]
Blood Pressure Cases: [number]
Respiratory Cases: [number]
"""
            
            print(f"Sending API request with {self.current_model_name} to analyze coordinates ({lat}, {lon})")
            
            # Improved retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"API attempt {attempt+1} with model: {self.current_model_name}")
                    
                    # Set a timeout to avoid hanging
                    response = await asyncio.wait_for(
                        self.api_client.generate_content_async(prompt),
                        timeout=45  # Increased timeout for better results
                    )
                    
                    if response and hasattr(response, 'text'):
                        response_text = response.text.strip()
                        print(f"API response received, length: {len(response_text)} characters")
                        print(f"First 50 chars: {response_text[:50]}...")
                        
                        # Parse the API response
                        lines = response_text.strip().split('\n')
                        data = {}
                        
                        # Expected fields in the response
                        expected_fields = [
                            "Total Population", "Economic Loss (INR)", "Houses Damaged", 
                            "Shops Damaged", "Hotels Damaged", "Schools Damaged",
                            "Children (%)", "Adults (%)", "Elderly (%)", "Male (%)", "Female (%)",
                            "Diabetes Cases", "Blood Pressure Cases", "Respiratory Cases"
                        ]
                        
                        # Process each line to extract numerical values
                        for line in lines:
                            line = line.strip()
                            if ":" in line:
                                parts = line.split(":", 1)
                                field = parts[0].strip()
                                value_str = parts[1].strip()
                                
                                # Find matching field
                                matching_field = None
                                for ef in expected_fields:
                                    if ef in field:
                                        matching_field = ef
                                        break
                                
                                if matching_field:
                                    try:
                                        # Extract numbers from value
                                        value_str = ''.join(c for c in value_str if c.isdigit() or c == '.')
                                        if value_str:
                                            if "(%)" in matching_field:
                                                data[matching_field] = float(value_str)
                                            else:
                                                data[matching_field] = int(float(value_str))
                                    except ValueError:
                                        print(f"Could not convert value for {matching_field}: {value_str}")
                        
                        # Check if we have most of the expected fields
                        if len(data) >= len(expected_fields) * 0.7:  # At least 70% of fields
                            # Fill in any missing fields with defaults
                            for field in expected_fields:
                                if field not in data:
                                    if "(%)" in field:
                                        data[field] = 33.3  # Default percentage
                                    elif "Economic Loss" in field:
                                        data[field] = 500000  # Default economic loss
                                    else:
                                        data[field] = 50  # Default for other numeric fields
                            
                            # Normalize percentage fields
                            self._normalize_percentages(data)
                            
                            print("Successfully parsed API data")
                            print(f"Population: {data.get('Total Population', 'N/A')}")
                            print(f"Houses Damaged: {data.get('Houses Damaged', 'N/A')}")
                            
                            return data
                        else:
                            print(f"Insufficient data fields in response: got {len(data)}/{len(expected_fields)}")
                    else:
                        print(f"Invalid response on attempt {attempt+1}")
                except asyncio.TimeoutError:
                    print(f"Request timed out on attempt {attempt+1}")
                except Exception as e:
                    print(f"API error on attempt {attempt+1}: {str(e)}")
                
                # Wait before retrying with exponential backoff
                await asyncio.sleep(1 * (attempt + 1))
                
            print("All API attempts failed")
            return None
        except Exception as e:
            print(f"API error: {str(e)}")
            return None
        
    def _normalize_percentages(self, data):
        """Ensure percentage values sum to 100%"""
        age_fields = ["Children (%)", "Adults (%)", "Elderly (%)"]
        gender_fields = ["Male (%)", "Female (%)"]
        
        # Normalize age percentages
        age_sum = sum(data.get(field, 0) for field in age_fields)
        if age_sum > 0 and abs(age_sum - 100) > 5:  # If more than 5% off from 100%
            factor = 100 / age_sum
            for field in age_fields:
                if field in data:
                    data[field] = round(data[field] * factor, 1)
        
        # Normalize gender percentages
        gender_sum = sum(data.get(field, 0) for field in gender_fields)
        if gender_sum > 0 and abs(gender_sum - 100) > 5:  # If more than 5% off from 100%
            factor = 100 / gender_sum
            for field in gender_fields:
                if field in data:
                    data[field] = round(data[field] * factor, 1)

    async def get_impact_data(self, lat, lon):
        # First try API if available
        if self.api_client:
            print(f"\n=== Attempting to fetch data from API using {self.current_model_name} ===")
            # Test API connection first
            api_available = await self.test_api_connection()
            
            if api_available:
                print("\n=== API connection successful, retrieving disaster impact data... ===")
                api_data = await self.get_data_from_api(lat, lon)
                if api_data:
                    print(f"\n=== Successfully fetched data from API using {self.current_model_name} ===")
                    # Print sample of the API data
                    print("API data sample:")
                    print(f"- Total Population: {api_data.get('Total Population', 'N/A')}")
                    print(f"- Economic Loss: {api_data.get('Economic Loss (INR)', 'N/A')}")
                    print(f"- Houses Damaged: {api_data.get('Houses Damaged', 'N/A')}")
                    return api_data, 'api', self.current_model_name
                print("\n=== API data retrieval failed, falling back to CSV ===")
            else:
                print("\n=== API connection test failed, falling back to CSV ===")
                # Reset API client to force re-initialization on next attempt
                self.api_client = None
                self.current_model_name = None
                self.init_api_client()

        # Fallback to CSV if API fails or not available
        print("\n=== Fetching data from CSV... ===")
        # Get nearest coordinates data from CSV
        if self.csv_loaded:
            print("Fetching data from CSV...")
            # Get nearest coordinates data from CSV
            if self.data is not None and not self.data.empty:
                # Calculate distances to find closest point
                if 'latitude' in self.data.columns and 'longitude' in self.data.columns:
                    # Calculate distance using Euclidean distance formula
                    self.data['distance'] = ((self.data['latitude'] - lat) ** 2 + 
                                           (self.data['longitude'] - lon) ** 2) ** 0.5
                    closest_idx = self.data['distance'].idxmin()
                    data = self.data.iloc[closest_idx].to_dict()
                    return data, 'csv', None  # Ensure we always return 3 values
                else:
                    # If latitude and longitude columns don't exist, just return the first row
                    data = self.data.iloc[0].to_dict()
                    return data, 'csv', None  # Ensure we always return 3 values
            else:
                raise Exception("CSV data is empty or not properly loaded")
        
        raise Exception("No data source available")
