# VC Copilot

An AI-powered tool for analyzing startup websites and providing comprehensive insights for venture capital decision-making.

## Features

- **Startup Analysis**
  - Automated website scraping and data extraction
  - Smart company information gathering
  - Modular analysis pipeline
  - Real-time progress tracking

- **Founder Intelligence**
  - Scientific criteria-based founder evaluation
  - Experience and track record analysis
  - Team composition assessment
  - Leadership potential scoring

- **Funding Research**
  - Funding history tracking
  - Investment round analysis
  - Key investor identification
  - Recent funding news aggregation

- **Deep Dive Reports**
  - Comprehensive startup evaluation
  - Market positioning analysis
  - Growth potential assessment
  - Executive summaries

## Tech Stack

### Backend
- FastAPI (Python 3.9+)
- OpenAI API integration
- BeautifulSoup and Playwright for web scraping
- Modular analysis pipelines
- Jupyter notebooks for testing

### Frontend
- Next.js 13+ with TypeScript
- Tailwind CSS for modern UI
- Zustand for state management
- Component-based architecture
- Progressive loading UI

### Architecture
- **Modular Design**
  - Independent analysis modules
  - Flexible data collection pipeline
  - Reusable UI components
  - Type-safe API integration

- **Core Features**
  - Real-time analysis progress
  - Comprehensive error handling
  - Responsive single-page design
  - Intuitive user experience

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/luisschmitz/VC-Copilot.git
cd VC-Copilot
```

2. Install frontend dependencies
```bash
cd frontend
npm install
```

3. Set up the backend
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure environment variables
```bash
# In backend/.env
OPENAI_API_KEY=your_api_key_here

# In frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Start the development servers

Backend:
```bash
# From the backend directory
python run_backend.py
```

Frontend:
```bash
# From the frontend directory
npm run dev
```

The application will be available at `http://localhost:3000`

## Development

### Project Structure

```
VC-Copilot/
├── backend/
│   ├── analysis.py      # Core analysis logic
│   ├── founder_info.py  # Founder evaluation
│   ├── funding_news.py  # Funding research
│   ├── main.py         # FastAPI application
│   └── scraping.py     # Web scraping
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── lib/       # Utilities and state
│   │   └── types/     # TypeScript definitions
│   └── public/
└── README.md
```

### Testing

The project includes a comprehensive Jupyter notebook (`vc_copilot_test.ipynb`) for testing all major features:
- Website scraping
- SWOT analysis
- Deep dive reports
- Founder evaluation
- Funding analysis

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.