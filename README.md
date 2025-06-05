# VC Copilot - Backend API

A backend API for analyzing startup websites and providing insights using AI.

## Features

- Website Scraping: Extract essential data from startup websites
- Executive Summary: Generate deep dive analysis of the startup
- Founder Success Prediction: Evaluate founders based on scientific criteria

## Tech Stack

### Backend
- FastAPI (Python) with simplified endpoints
- OpenAI API for executive summary and founder evaluation
- No database dependency (stateless API)

### Architecture
- Modular design with core components:
  - Website scraper module
  - Deep dive analysis module
  - Founder success prediction module
- Simplified API with a single `/analyze` endpoint
- Robust error handling and fallback mechanisms for API calls

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/luisschmitz/VC-Copilot.git
cd VC-Copilot
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cd backend
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run the backend server
```bash
python run_backend.py
```

## API Usage

### Analyze Endpoint
```
POST /analyze
```

Request body:
```json
{
  "url": "https://example-startup.com"
}
```

Response:
```json
{
  "company_name": "Example Startup",
  "executive_summary": "...",
  "key_insights": ["...", "..."],
  "key_risks": ["...", "..."],
  "success_prediction": "High",
  "overall_assessment": "...",
  "evaluation_criteria": {...}
}
```

## Testing

### Interactive Testing
Use the provided Jupyter notebook to test the functionality:
- `vc_copilot_test.ipynb`: Tests the backend API functionality

## License

MIT