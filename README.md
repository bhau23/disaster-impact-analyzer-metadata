# Disaster Impact Analyzer

![Disaster Impact Analyzer](https://img.shields.io/badge/Disaster-Impact_Analyzer-5A2AFF)
![Version](https://img.shields.io/badge/Version-3.0-blue)

A sophisticated tool designed to predict and visualize the impact of disasters on communities in Chhattisgarh, India. This application helps government agencies and disaster management teams with better preparation and resource allocation through data-driven insights.

## Features

- **Real-time Impact Assessment**: Uses Google's Gemini AI models to generate disaster impact predictions based on location
- **Offline Fallback Mode**: Seamlessly switches to CSV-based data when API is unavailable
- **Interactive Map Selection**: Click-to-select location functionality with coordinate input options
- **Comprehensive Analysis**:
  - Population demographics (age groups, gender distribution)
  - Health impact estimation (medical conditions, required response)
  - Infrastructure damage assessment (buildings, economic impact)
- **Data Source Transparency**: Clear references to data sources used in predictions
- **Export Options**: Download reports in CSV and JSON formats

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd diasaster_impact
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment variables:
   Create a `.env` file in the `meta_model` directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   You can get a Gemini API key from [Google AI Studio](https://ai.google.dev/).

## Usage

1. Start the application:
   ```bash
   cd meta_model
   streamlit run app.py
   ```

2. Access the web interface at `http://localhost:8501`

3. Use the application:
   - Select a location on the map or enter coordinates
   - Choose disaster type and impact radius
   - Click "Generate Impact Report"
   - Explore the visualizations and analysis in the main panel

## Data Sources

The application uses multiple data sources:

### Primary Sources
- **Google Gemini AI** - For real-time disaster impact predictions
- **Chhattisgarh Disaster Dataset** - CSV data for offline mode with coordinates-based matching

### Referenced Sources (for API-generated data)
- Census of India (Demographics)
- Chhattisgarh State Disaster Management Authority (Regional Data)
- National Health Mission - Chhattisgarh (Health Data)
- Disaster-specific data sources (varies by disaster type)

## Architecture

```
diasaster_impact/
├── meta_model/                # Main application directory
│   ├── app.py                 # Streamlit UI and main application logic
│   ├── model.py               # Disaster impact model with API/CSV handling
│   ├── diagnostics.py         # API connection diagnostics tool
│   ├── async_utils.py         # Async utilities for API communication
│   ├── .env                   # Environment variables (API keys)
│   └── chhattisgarh_disaster_metadata_regenerated(new2).csv  # Backup dataset
└── README.md                  # Project documentation
```

## System Requirements

- **Model**: Google Gemini AI (1.5-pro or other compatible models)
- **Memory**: 4GB+ RAM recommended
- **Storage**: 100MB free space
- **Internet**: Required for API mode (optional for CSV-only mode)

## API Settings

The application tries to connect to the following Gemini models in order:
1. gemini-1.5-pro
2. models/gemini-1.5-flash-latest
3. models/gemini-1.5-pro-latest
4. models/gemini-pro-latest
5. gemini-pro

You can use the API reconnection option in the interface if the connection fails.

## Troubleshooting

- **API Not Connecting**: Verify your API key in the `.env` file and ensure internet connectivity
- **Map Not Working**: Ensure you have a stable internet connection for the map tiles to load
- **Slow Performance**: Try reducing the impact radius or switch to CSV mode for faster results

## License

[Specify your license here]

## Acknowledgements

- Google AI for the Gemini API
- Streamlit for the web application framework
- Folium for the interactive maps
- Plotly for the visualization components
