# VC Copilot

A tool to analyze startup websites and provide insights using AI.

## Features

- URL Analysis: Input a startup website URL
- Web Scraping: Extract company information, team details, and product descriptions
- AI Analysis: Leverage GPT to analyze the collected data
- Results Storage: Save and retrieve past analyses
- Export: Download results as PDF or JSON

## Tech Stack

### Frontend
- Next.js with React
- Deployed on Vercel (Free Tier)
- Static site generation and serverless functions

### Backend
- FastAPI (Python) or Next.js API routes
- PostgreSQL database on Railway (Free Tier)
- OpenAI API for analysis

### Data Storage
- Railway PostgreSQL for structured data
- GitHub repository as CDN for static assets

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL (for local development)

### Installation

1. Clone the repository
```bash
git clone https://github.com/luisschmitz/VC-Copilot.git
cd VC-Copilot
```

2. Install frontend dependencies
```bash
npm install
```

3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# For frontend
cp .env.example .env

# For backend
cd backend
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. Run the development server
```bash
# Start the frontend
npm run dev

# In a separate terminal, start the backend
cd backend
python main.py
```

## Usage

1. Navigate to the application in your browser
2. Enter a startup website URL
3. View the analysis results
4. Export or save the results as needed

## License

MIT