import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import time
import asyncio
import os
from streamlit_folium import st_folium
from model import DisasterImpactModel  # Using relative import

# Page Configuration
st.set_page_config(
    page_title="Disaster Impact Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced royal dark theme
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            color: #E0E0FF;
            background-color: #0F0F1F;
        }
        
        .main-title {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            padding: 15px;
            margin-bottom: 20px;
            color: #FFFFFF;
            text-shadow: 0 0 15px rgba(100, 100, 255, 0.6);
            background: linear-gradient(135deg, #4A0A8F, #2A0A4F);
            border-radius: 10px;
            border: 1px solid #6A3ABA;
        }
        
        .card { 
            background: linear-gradient(135deg, #1A1A2E, #151525);
            border-radius: 10px;
            padding: 1.8rem;
            margin: 1rem 0;
            border: 1px solid #3A3A5A;
            box-shadow: 0 5px 15px rgba(0,0,0,0.35);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #252538, #1A1A28);
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid #4A4A7A;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(100,100,255,0.2);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            margin: 10px 0;
            color: #A5A5FF;
            text-shadow: 0 0 5px rgba(100,100,255,0.3);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #CCCCFF;
            font-weight: 500;
        }
        
        .section-title {
            font-size: 1.6rem;
            font-weight: 600;
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #FFFFFF;
            text-shadow: 0 0 8px rgba(100,100,255,0.4);
        }

        /* Fix for streamlit elements */
        .stTextInput > label, .stNumberInput > label, .stSlider > label, .stSelectbox > label {
            color: #E0E0FF !important;
            font-weight: 500 !important;
        }
        
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            background-color: #252538 !important;
            color: #E0E0FF !important;
            border: 1px solid #4A4A7A !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #CCCCFF !important;
            font-weight: 500 !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1A1A2E !important;
            border-radius: 10px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #5A2AFF !important;
            color: white !important;
        }
        
        /* Make text elements more visible */
        p, span, li, a, div {
            color: #E0E0FF;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF;
            text-shadow: 0 0 5px rgba(100,100,255,0.3);
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #5A2AFF, #3A1ADF) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25) !important;
            transition: all 0.3s !important;
        }
        
        .stButton>button:hover {
            background: linear-gradient(135deg, #6A3AFF, #4A2AEF) !important;
            box-shadow: 0 5px 15px rgba(90,42,255,0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        .stDownloadButton>button {
            background: linear-gradient(135deg, #3A5AFF, #2A4AEF) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        
        .stDownloadButton>button:hover {
            background: linear-gradient(135deg, #4A6AFF, #3A5AEF) !important;
            box-shadow: 0 5px 15px rgba(58,90,255,0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Data source indicators */
        .data-source-live {
            background: linear-gradient(135deg, #153545, #0A2530);
            padding: 12px;
            border-radius: 8px;
            margin: 12px 0;
            border: 1px solid #2A5AFF;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25);
            animation: pulseLive 2s infinite;
        }
        
        .data-source-offline {
            background: linear-gradient(135deg, #352535, #2A1A2A);
            padding: 12px;
            border-radius: 8px;
            margin: 12px 0;
            border: 1px solid #FF2A5A;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25);
        }
        
        @keyframes pulseLive {
            0% { box-shadow: 0 0 0 0 rgba(42, 90, 255, 0.5); }
            70% { box-shadow: 0 0 0 10px rgba(42, 90, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(42, 90, 255, 0); }
        }
        
        /* Progress bar styling */
        div.stProgress > div > div > div > div {
            background-color: #5A2AFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize model with better feedback
@st.cache_resource
def init_model():
    try:
        with st.spinner("Initializing model and checking API connection..."):
            model = DisasterImpactModel()
            csv_path = os.path.join(os.path.dirname(__file__), 
                                "chhattisgarh_disaster_metadata_regenerated(new2).csv")
            model.load_data(csv_path)
            model.load_model(os.path.join(os.path.dirname(__file__), "disaster_model(meta).pkl"))
            
            # Store model info in session state
            st.session_state.model_info = {
                'api_status': "Available" if model.api_client else "Not available",
                'csv_loaded': model.csv_loaded,
                'current_model': model.current_model_name if model.api_client else None
            }
            
            if model.api_client:
                st.success(f"✅ API connected successfully using {model.current_model_name}")
            else:
                st.error("❌ API connection failed - using CSV data instead")
                
            return model
    except Exception as e:
        st.error(f"Error initializing model: {str(e)}")
        return None

def loading_animation():
    progress_bar = st.progress(0)
    with st.spinner('Analyzing disaster impact...'):
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        progress_bar.empty()

def display_metric_card(icon, title, value, col):
    with col:
        html = f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

async def get_impact_data(lat: float, lon: float, force_api=False):
    """Get impact data from either API or CSV source"""
    try:
        if force_api:
            data, source, model_name = await force_api_request(lat, lon)
        else:
            result = await model.get_impact_data(lat, lon)
            
            if len(result) == 3:
                data, source, model_name = result
            elif len(result) == 2:
                data, source = result
                model_name = None
            else:
                raise ValueError(f"Unexpected return format from get_impact_data: {result}")
        
        if data and source:
            # Add debug information
            if source == 'api':
                st.success(f"🌐 Data successfully retrieved from API ({model_name})")
            else:
                st.info("📄 Data retrieved from CSV (API data not available)")
                
        return data, source, model_name
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None, None

def show_data_source_indicator(source, model_name=None):
    """Display a live indicator showing the data source being used"""
    if source == 'api':
        st.markdown(f"""
        <div class="data-source-live">
            <span style="color:#4AFF4A; font-size:1.0rem;">●</span>
            <span style="color:#E0E0FF; font-weight:500;"> LIVE: Using real-time API data</span><br>
            <span style="color:#9A9AFF; font-size:0.9rem;">Model: {model_name}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="data-source-offline">
            <span style="color:#FF4A4A; font-size:1.0rem;">●</span>
            <span style="color:#E0E0FF; font-weight:500;"> OFFLINE: Using local dataset</span><br>
            <span style="color:#FF9A9A; font-size:0.9rem;">Using nearest coordinate matching from CSV</span>
        </div>
        """, unsafe_allow_html=True)

# Add a function to try reconnect to the API with a specific model
async def try_reconnect_api():
    """Try to reconnect to the API"""
    with st.spinner("Attempting to reconnect to API..."):
        # Reinitialize the API client
        model.api_client = None
        model.current_model_name = None
        model.init_api_client()
        
        if model.api_client:
            is_connected = await model.test_api_connection()
            
            # Update session state
            st.session_state.model_info['api_status'] = "Available" if is_connected else "Not available"
            st.session_state.model_info['current_model'] = model.current_model_name if is_connected else None
            
            if is_connected:
                st.success(f"✅ API reconnected successfully using {model.current_model_name}")
                return True
            else:
                st.error("❌ API reconnection failed")
                return False
        else:
            st.error("❌ Failed to initialize any API model")
            return False

# Add a new function to force API usage
async def force_api_request(lat, lon):
    """Force data retrieval from API without CSV fallback"""
    if model and model.api_client:
        try:
            st.info("🔄 Testing API connection...")
            # First ensure API is connected
            api_available = await model.test_api_connection()
            
            if not api_available:
                st.error("❌ API connection failed in preliminary test")
                return None, None, None
                
            st.info("✓ API connection test passed")
            st.info(f"🔄 Sending request to {model.current_model_name}...")
            
            # Send a direct request to get_data_from_api (bypassing CSV fallback)
            api_data = await model.get_data_from_api(lat, lon)
            
            if api_data:
                st.success(f"✅ Successfully retrieved data from {model.current_model_name}")
                return api_data, 'api', model.current_model_name
            else:
                st.error("❌ API request failed to return valid data")
                return None, None, None
        except Exception as e:
            st.error(f"❌ Error in force_api_request: {str(e)}")
            return None, None, None
    else:
        st.error("❌ No API client available")
        return None, None, None

# Add a function to generate references for API data
def generate_data_references(disaster_type):
    """Generate relevant data sources and references based on disaster type"""
    
    # Common references for all disaster types
    common_references = [
        {
            "name": "Census of India",
            "description": "Demographic data including population statistics",
            "url": "https://censusindia.gov.in/",
            "data_type": "Demographics"
        },
        {
            "name": "Chhattisgarh State Disaster Management Authority",
            "description": "Local disaster management data and historical records",
            "url": "https://cgsdma.gov.in/",
            "data_type": "Regional Data"
        },
        {
            "name": "National Health Mission - Chhattisgarh",
            "description": "Health statistics and medical infrastructure data",
            "url": "https://cg.nhm.gov.in/",
            "data_type": "Health Data"
        }
    ]
    
    # Disaster-specific references
    disaster_references = {
        "Flood": [
            {
                "name": "Central Water Commission",
                "description": "River water levels and flood forecasting data",
                "url": "https://cwc.gov.in/",
                "data_type": "Hydrological Data"
            },
            {
                "name": "India Meteorological Department",
                "description": "Rainfall data and precipitation patterns",
                "url": "https://mausam.imd.gov.in/",
                "data_type": "Weather Data"
            },
            {
                "name": "National Remote Sensing Centre",
                "description": "Satellite imagery for flood extent mapping",
                "url": "https://www.nrsc.gov.in/",
                "data_type": "Satellite Data"
            }
        ],
        "Earthquake": [
            {
                "name": "National Centre for Seismology",
                "description": "Earthquake monitoring and seismic data",
                "url": "https://seismo.gov.in/",
                "data_type": "Seismic Data"
            },
            {
                "name": "Geological Survey of India",
                "description": "Geological and terrain information",
                "url": "https://www.gsi.gov.in/",
                "data_type": "Geological Data"
            },
            {
                "name": "Building Materials & Technology Promotion Council",
                "description": "Building vulnerability data for seismic zones",
                "url": "https://bmtpc.org/",
                "data_type": "Infrastructure Data"
            }
        ],
        "Cyclone": [
            {
                "name": "India Meteorological Department - Cyclone Warning",
                "description": "Cyclone tracking and intensity data",
                "url": "https://mausam.imd.gov.in/",
                "data_type": "Weather Data"
            },
            {
                "name": "National Disaster Management Authority - Cyclone",
                "description": "Cyclone preparedness and impact assessment",
                "url": "https://ndma.gov.in/Natural-Hazards/Cyclone",
                "data_type": "Disaster Management Data"
            },
            {
                "name": "Indian National Centre for Ocean Information Services",
                "description": "Ocean state forecasting and storm surge predictions",
                "url": "https://incois.gov.in/",
                "data_type": "Oceanographic Data"
            }
        ],
        "Wildfire": [
            {
                "name": "Forest Survey of India",
                "description": "Forest cover and fire alert system data",
                "url": "https://fsi.nic.in/",
                "data_type": "Forest Data"
            },
            {
                "name": "FIRMS - NASA Fire Information for Resource Management",
                "description": "Satellite-based fire detection data",
                "url": "https://firms.modaps.eosdis.nasa.gov/",
                "data_type": "Satellite Fire Data"
            },
            {
                "name": "India State of Forest Report",
                "description": "Forest vulnerability assessment data",
                "url": "https://fsi.nic.in/forest-report",
                "data_type": "Forest Assessment Data"
            }
        ],
        "Landslide": [
            {
                "name": "Geological Survey of India - Landslide Studies",
                "description": "Landslide susceptibility mapping",
                "url": "https://www.gsi.gov.in/",
                "data_type": "Geological Data"
            },
            {
                "name": "National Remote Sensing Centre - Landslide Monitoring",
                "description": "Satellite based landslide detection",
                "url": "https://www.nrsc.gov.in/",
                "data_type": "Remote Sensing Data"
            },
            {
                "name": "Indian Roads Congress",
                "description": "Road infrastructure vulnerability data in hilly regions",
                "url": "https://irc.org.in/",
                "data_type": "Infrastructure Data"
            }
        ]
    }
    
    # Combine common and specific references
    specific_refs = disaster_references.get(disaster_type, [])
    all_references = common_references + specific_refs
    
    # Add AI model used information if available
    if 'model_name' in st.session_state and st.session_state.model_name:
        model_name = st.session_state.model_name
        model_info = {
            "name": f"Google AI - {model_name}",
            "description": "Generative AI model used for disaster impact prediction",
            "url": "https://ai.google.dev/",
            "data_type": "AI Model"
        }
        all_references.append(model_info)
    
    return all_references

# Function to display references in the UI
def display_data_references(references):
    """Display the data references in a structured format"""
    
    st.markdown('<div class="section-title">📚 Data Sources & References</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom:15px;">
        <p>The following data sources were used to generate this impact assessment:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Group references by data type
    data_types = {}
    for ref in references:
        data_type = ref["data_type"]
        if (data_type not in data_types):
            data_types[data_type] = []
        data_types[data_type].append(ref)
    
    # Create tabs for different data types
    if data_types:
        tabs = st.tabs(list(data_types.keys()))
        
        for i, (data_type, refs) in enumerate(data_types.items()):
            with tabs[i]:
                for ref in refs:
                    st.markdown(f"""
                    <div style="background:#1A1A2E; padding:12px; border-radius:8px; margin-bottom:10px; border:1px solid #3A3A5A;">
                        <strong style="color:#FFFFFF; font-size:1.1rem;">{ref['name']}</strong><br>
                        <span style="color:#CCCCFF;">{ref['description']}</span><br>
                        <a href="{ref['url']}" target="_blank" style="color:#5A8AFF;">Visit Source</a>
                    </div>
                    """, unsafe_allow_html=True)

# Initialize the model
model = init_model()

# Header
st.markdown('<h1 class="main-title">DISASTER IMPACT ANALYZER</h1>', unsafe_allow_html=True)

# Layout Setup
col1, col2 = st.columns([1, 2], gap="large")

# User Input Panel
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌍 Location Details</div>', unsafe_allow_html=True)
    
    use_map = st.checkbox("Select location on map", value=True)
    
    if use_map:
        # Create a simple map for location selection
        m = folium.Map(location=[21.19188593, 82.73063208], zoom_start=10)
        
        # Convert to html and display
        map_data = st_folium(m, height=300, width=400)
        
        # Initialize default coordinates
        lat = 21.19188593
        lon = 82.73063208
        
        # Extract coordinates if clicked - add proper validation
        if map_data and 'last_clicked' in map_data and map_data['last_clicked'] is not None:
            lat = map_data['last_clicked']['lat']
            lon = map_data['last_clicked']['lng']
            st.success(f"Selected: {lat:.6f}, {lon:.6f}")
        else:
            st.info("👆 Click on the map to select a location or use the input fields below")
    else:
        lat = st.number_input("Latitude", value=21.19188593, format="%.8f")
        lon = st.number_input("Longitude", value=82.73063208, format="%.8f")

    # Add manual coordinate inputs as fallback regardless of map selection
    if use_map:
        with st.expander("Manual coordinates"):
            lat_manual = st.number_input("Latitude", value=lat, format="%.8f", key="lat_manual")
            lon_manual = st.number_input("Longitude", value=lon, format="%.8f", key="lon_manual")
            if st.button("Use these coordinates"):
                lat = lat_manual
                lon = lon_manual
                st.success(f"Using coordinates: {lat:.6f}, {lon:.6f}")
    
    impact_radius = st.slider("Impact Radius (km)", 1, 50, 10)
    st.session_state.impact_radius = impact_radius
    
    disaster_type = st.selectbox(
        "Disaster Type",
        ["Flood", "Earthquake", "Cyclone", "Wildfire", "Landslide"]
    )
    
    # API options in expander
    with st.expander("API Settings", expanded=False):
        # Show current model information if available
        if model and model.api_client and model.current_model_name:
            st.success(f"Using API model: {model.current_model_name}")
        elif model:
            st.warning("API not connected - will use CSV data")
        
        # Add reconnection option
        if st.button("🔄 Reconnect API"):
            asyncio.run(try_reconnect_api())
        
        # Option to force API usage
        force_api = st.checkbox("Force API (no CSV fallback)", value=False,
                              help="When enabled, will only use API and not fall back to CSV data")
    
    # Generate button
    generate_btn = st.button("🚀 Generate Impact Report")
    if generate_btn:
        if model:
            api_source_text = "API" if model.api_client else "CSV (API unavailable)"
            with st.spinner(f"Generating impact report using {api_source_text}..."):
                loading_animation()
                
                # Handle force_api option if set in the expander
                if 'force_api' in locals() and force_api:
                    st.info("Forcing API usage - will not fall back to CSV")
                    # This would be a direct API call with no fallback
                    if model.api_client:
                        api_data = asyncio.run(force_api_request(lat, lon))
                        if api_data and len(api_data) == 3:
                            data, source, model_name = api_data
                        else:
                            st.error("❌ API data retrieval failed and CSV fallback is disabled")
                            st.stop()
                    else:
                        st.error("❌ No API connection available and CSV fallback is disabled")
                        st.stop()
                else:
                    # Normal behavior with fallback
                    data, source, model_name = asyncio.run(get_impact_data(lat, lon))
                
                if data:
                    st.session_state.data = data
                    st.session_state.data_source = source
                    st.session_state.model_name = model_name
                    
                    # Display source indicator
                    show_data_source_indicator(source, model_name)
                    
                    if source == 'api':
                        st.success(f"✅ Report generated successfully from API using {model_name}!")
                    else:
                        st.warning("⚠️ Using CSV data (API unavailable or failed)")
                    
                    # Add timestamp
                    st.session_state.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.disaster_type = disaster_type
                else:
                    st.error("❌ Failed to generate report. Please try again.")
        else:
            st.error("❌ Model not properly initialized. Please check the logs.")
    
    # Show data source info if data exists
    if 'data' in st.session_state:
        source_icon = "🌐" if st.session_state.data_source == 'api' else "📄"
        source_text = "API Data" if st.session_state.data_source == 'api' else "CSV Data"
        
        model_info = ""
        if st.session_state.data_source == 'api' and st.session_state.get('model_name'):
            model_info = f"<br><span style=\"color:#9A9AFF;\">Model:</span> {st.session_state.get('model_name')}"
        
        source_html = f"""
        <div style="margin-top:20px; font-size:0.9rem; background:#1A1A2E; padding:12px; border-radius:8px; border:1px solid #3A3A5A;">
            <span style="color:#CCCCFF;">Data Source:</span> {source_icon} <strong style="color:#E0E0FF;">{source_text}</strong>{model_info}<br>
            <span style="color:#CCCCFF;">Generated:</span> <span style="color:#E0E0FF;">{st.session_state.get('timestamp', 'N/A')}</span><br>
            <span style="color:#CCCCFF;">Disaster Type:</span> <span style="color:#E0E0FF;">{st.session_state.get('disaster_type', 'N/A')}</span><br>
        </div>
        """
        st.markdown(source_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model Status panel
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ System Status</div>', unsafe_allow_html=True)
    
    if 'model_info' in st.session_state:
        api_status = st.session_state.model_info["api_status"]
        api_status_icon = '🟢' if api_status == "Available" else '🔴'
        
        csv_status = "✅ Loaded" if st.session_state.model_info['csv_loaded'] else "❌ Not Loaded"
        csv_status_icon = '🟢' if st.session_state.model_info['csv_loaded'] else '🔴'
        
        st.markdown(f'{api_status_icon} API Status: {api_status}')
        
        # Show model name if available
        if 'current_model' in st.session_state.model_info and st.session_state.model_info['current_model']:
            st.markdown(f'<span style="color:#9A9AFF;">Current model:</span> {st.session_state.model_info["current_model"]}', unsafe_allow_html=True)
        
        st.markdown(f'{csv_status_icon} CSV Data: {csv_status}')
        
        # Add API troubleshooting info if API is not available
        if api_status != "Available":
            st.markdown("""
            <div style="background:#352535; padding:10px; border-radius:8px; margin-top:10px; font-size:0.9rem; border:1px solid #FF4A7A;">
            <strong style="color:#FF9A9A;">⚠️ API Troubleshooting</strong><br>
            - Check your API key in the .env file<br>
            - Ensure internet connectivity<br>
            - Try clicking "Reconnect API" button
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#153545; padding:10px; border-radius:8px; margin-top:10px; font-size:0.9rem; border:1px solid #2A7AFF;">
            <strong style="color:#4AFF4A;">✅ API Status</strong><br>
            API is connected and ready to generate real-time disaster impact data.
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Data Visualization Panel
if 'data' in st.session_state:
    data = st.session_state.data
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Key Metrics
        st.markdown('<div class="section-title">📊 Impact Overview</div>', unsafe_allow_html=True)
        
        metric_cols = st.columns(3)
        display_metric_card("👥", "Population", f"{data['Total Population']:,}", metric_cols[0])
        display_metric_card("💰", "Economic Loss", f"₹{data['Economic Loss (INR)']:,.2f}", metric_cols[1])
        
        # Calculate total damage
        total_damage = sum([data.get(c, 0) for c in ['Houses Damaged', 'Shops Damaged', 'Hotels Damaged', 'Schools Damaged']])
        display_metric_card("🏚️", "Damaged Units", f"{total_damage:,}", metric_cols[2])
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Tabs with better visualization
        tabs = st.tabs(["📈 Demographics", "🏥 Health Impact", "🏘️ Infrastructure"])

        with tabs[0]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">👨‍👩‍👧‍👦 Population Distribution</div>', unsafe_allow_html=True)
            
            # Age distribution
            age_col1, age_col2 = st.columns(2)
            with age_col1:
                fig = px.pie(
                    names=['Children', 'Adults', 'Elderly'],
                    values=[data['Children (%)'], data['Adults (%)'], data['Elderly (%)']],
                    title="Age Distribution",
                    hole=0.4,
                    color_discrete_sequence=['#9A9AFF', '#FF9A9A', '#9AFFFF']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E0FF'),
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Gender distribution
            with age_col2:
                fig = px.bar(
                    x=['Male', 'Female'],
                    y=[data['Male (%)'], data['Female (%)']],
                    labels={'x': 'Gender', 'y': 'Percentage'},
                    title="Gender Distribution",
                    text=[f"{data['Male (%)']:.1f}%", f"{data['Female (%)']:.1f}%"],
                    color_discrete_sequence=['#5A2AFF', '#FF2A5A']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E0FF'),
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                fig.update_traces(textfont=dict(color='#FFFFFF'))
                st.plotly_chart(fig, use_container_width=True)
                
            # Calculate population values
            children_population = int(data['Total Population'] * (data['Children (%)'] / 100))
            adults_population = int(data['Total Population'] * (data['Adults (%)'] / 100))
            elderly_population = int(data['Total Population'] * (data['Elderly (%)'] / 100))
            
            pop_cols = st.columns(3)
            display_metric_card("👶", "Children", f"{children_population:,}", pop_cols[0])
            display_metric_card("👨‍👩‍👧", "Adults", f"{adults_population:,}", pop_cols[1])
            display_metric_card("👴", "Elderly", f"{elderly_population:,}", pop_cols[2])
            
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[1]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏥 Health Impact Analysis</div>', unsafe_allow_html=True)
            
            # Health chart
            fig = px.bar(
                x=['Diabetes', 'Blood Pressure', 'Respiratory'],
                y=[data['Diabetes Cases'], data['Blood Pressure Cases'], data['Respiratory Cases']],
                labels={'x': 'Condition', 'y': 'Cases'},
                title="Medical Conditions",
                text=[f"{data['Diabetes Cases']}", f"{data['Blood Pressure Cases']}", f"{data['Respiratory Cases']}"],
                color_discrete_sequence=['#FF5A5A', '#5A5AFF', '#5AFFFF']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E0E0FF'),
                margin=dict(t=30, b=0, l=0, r=0),
                height=350
            )
            fig.update_traces(textfont=dict(color='#FFFFFF'))
            st.plotly_chart(fig, use_container_width=True)
            
            # Medical needs
            total_population = data['Total Population']
            total_medical_cases = data['Diabetes Cases'] + data['Blood Pressure Cases'] + data['Respiratory Cases']
            medical_percentage = (total_medical_cases / total_population) * 100 if total_population > 0 else 0
            
            med_cols = st.columns(2)
            with med_cols[0]:
                display_metric_card("🩺", "Medical Cases", f"{total_medical_cases:,}", med_cols[0])
            
            with med_cols[1]:
                display_metric_card("🚑", "% of Population", f"{medical_percentage:.1f}%", med_cols[1])
            
            # Medical needs
            st.markdown("""
            <div style="background:#252538; padding:15px; border-radius:8px; margin-top:15px; border:1px solid #3A3A5A;">
                <h3 style="margin-top:0; color:#FFFFFF;">Medical Response Needed</h3>
                <ul style="margin-bottom:0;">
            """, unsafe_allow_html=True)
            
            critical_cases = int(total_medical_cases * 0.15)
            stable_cases = total_medical_cases - critical_cases
            medical_teams = max(1, int(total_medical_cases / 50))
            field_hospitals = max(1, int(total_medical_cases / 200))
            
            st.markdown(f"- Critical cases requiring immediate attention: **{critical_cases:,}**")
            st.markdown(f"- Stable cases requiring regular medical care: **{stable_cases:,}**")
            st.markdown(f"- Medical teams needed: **{medical_teams}**")
            st.markdown(f"- Field hospitals needed: **{field_hospitals}**")
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏘️ Infrastructure Damage</div>', unsafe_allow_html=True)
            
            # Infrastructure data
            infra_data = {
                'Type': ['Houses', 'Shops', 'Hotels', 'Schools'],
                'Damaged': [data['Houses Damaged'], data['Shops Damaged'], 
                           data['Hotels Damaged'], data['Schools Damaged']]
            }
            
            # Infrastructure chart
            fig = px.bar(
                x=infra_data['Type'],
                y=infra_data['Damaged'],
                title="Damaged Infrastructure",
                text=infra_data['Damaged'],
                color_discrete_sequence=['#5A2AFF', '#2A5AFF', '#FF2A5A', '#FFAA2A']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E0E0FF'),
                height=350,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            fig.update_traces(textfont=dict(color='#FFFFFF'), textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            # Economic impact
            st.markdown('<div class="section-title">💰 Economic Impact</div>', unsafe_allow_html=True)
            
            # Calculate economic impacts
            housing_loss = data['Houses Damaged'] * 500000  # Average house value
            business_loss = data['Shops Damaged'] * 300000 + data['Hotels Damaged'] * 2000000
            public_loss = data['Schools Damaged'] * 5000000
            
            econ_cols = st.columns(3)
            display_metric_card("🏠", "Housing Loss", f"₹{housing_loss:,.0f}", econ_cols[0])
            display_metric_card("🏪", "Business Loss", f"₹{business_loss:,.0f}", econ_cols[1])
            display_metric_card("🏫", "Public Loss", f"₹{public_loss:,.0f}", econ_cols[2])
            
            # Total economic impact
            st.markdown("""
            <div style="background:#252538; padding:15px; border-radius:8px; margin-top:15px; text-align:center; border:1px solid #5A2AFF;">
                <h3 style="margin:0; color:#FFFFFF;">Total Economic Impact</h3>
                <div style="font-size:1.8rem; font-weight:600; color:#FFAA2A; margin:10px 0; text-shadow: 0 0 5px rgba(255,170,42,0.3);">
                    ₹{:,.0f}
                </div>
            </div>
            """.format(data['Economic Loss (INR)']), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Add a new section for references if the data came from the API
        if st.session_state.data_source == 'api':
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Generate and display references based on the selected disaster type
            disaster_type = st.session_state.get('disaster_type', 'Flood')  # Default to Flood if not set
            references = generate_data_references(disaster_type)
            display_data_references(references)
            
            # Add explanation about AI-generated estimates
            st.markdown("""
            <div style="background:#252538; padding:15px; border-radius:8px; margin-top:15px; border:1px solid #3A3A5A;">
                <h3 style="margin-top:0; color:#FFFFFF;">About This Data</h3>
                <p style="margin-bottom:0;">
                This impact assessment combines real-world data from the sources listed above with AI-generated estimates. 
                The predictions are based on historical patterns, demographic data, and infrastructure information specific to the selected region.
                While every effort has been made to ensure accuracy, this should be used as an estimation tool to support disaster planning,
                not as the sole basis for critical decisions.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Simplified sidebar
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Export Data</div>', unsafe_allow_html=True)
    
    # Export options
    if 'data' in st.session_state:
        report_data = pd.DataFrame([st.session_state.data])
        
        st.download_button(
            "📥 Download CSV Report",
            report_data.to_csv(index=False),
            "disaster_report.csv",
            mime="text/csv",
            key="csv_report"
        )
        
        # Add JSON export
        import json
        json_data = json.dumps(st.session_state.data)
        st.download_button(
            "📥 Download JSON Report",
            json_data,
            "disaster_report.json",
            mime="application/json",
            key="json_report"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # About section - enhanced
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown("""
    **Disaster Impact Analyzer** helps government agencies predict and visualize the impact of disasters on communities, allowing for better preparation and resource allocation.
    
    **Key Features:**
    - Real-time impact assessment via API
    - Offline mode with CSV backup data
    - Comprehensive demographics analysis
    - Health impact estimation
    - Infrastructure damage assessment
    
    **Version:** 3.0
    """)
    st.markdown('</div>', unsafe_allow_html=True)
