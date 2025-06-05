# VC Copilot

An AI-powered tool for analyzing startup websites and providing insights for venture capital decision-making.

## Features

- Website Scraping: Extract essential data from startup websites
- Executive Summary: Generate deep dive analysis of the startup
- Founder Success Prediction: Evaluate founders based on scientific criteria
- Modern Web Interface: User-friendly dashboard for analysis results

## Tech Stack

### Backend
- FastAPI (Python) with simplified endpoints
- OpenAI API for executive summary and founder evaluation
- Web scraping with BeautifulSoup and Playwright

### Frontend
- Next.js with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- React components for UI

### Architecture
- Modular design with core components:
  - Website scraper module
  - Deep dive analysis module
  - Founder success prediction module
- Simplified API with a single `/analyze` endpoint
- Responsive UI with dashboard for viewing results

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm/yarn
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/luisschmitz/VC-Copilot.git
cd VC-Copilot
```

2. Set up the backend
```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Set up environment variables
cd backend
cp .env.example .env  # If .env.example exists, otherwise create a new .env file
# Edit .env and add your OpenAI API key
cd ..
```

3. Set up the frontend
```bash
cd frontend
npm install
# or if you use yarn
# yarn install
```

4. Run the application
```bash
# In one terminal, start the backend server
python run_backend.py

# In another terminal, start the frontend development server
python run_frontend.py
# or directly with npm
# cd frontend && npm run dev
```

5. Access the application
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000

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