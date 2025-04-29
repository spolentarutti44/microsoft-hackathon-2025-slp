# Nonprofit Grant Writer

A multi-agent system optimized to write grant applications for non-profit organizations based out of America.

## Overview

This application uses multiple AI agents to help nonprofit organizations create high-quality grant applications. It features:

- A user-friendly web interface for inputting organization and grant information
- Multiple specialized AI agents working together to research, write, and review grant content
- Integration with Azure OpenAI and Semantic Kernel for powerful AI capabilities
- Rich editing capabilities for reviewing and customizing the generated content
- Export to DOCX for final submission

## Tech Stack

- **Backend**: Python with Flask
- **AI Framework**: Microsoft Semantic Kernel
- **Orchestration**: MagenticOne (part of Semantic Kernel)
- **AI Services**: Azure OpenAI
- **Vector Database**: Qdrant (optional)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap and Quill.js

## Agent System

The application utilizes several specialized agents:

- **OrchestratorAgent**: Coordinates all other agents
- **ResearcherAgent**: Finds information about grants and nonprofits
- **WriterAgent**: Creates compelling grant content
- **NonProfitGroundingAgent**: Ensures content aligns with the nonprofit's mission
- **QualityCheckingAgent**: Evaluates and improves grant quality
- **ScraperAgent**: Extracts information from websites
- **WebSurferAgent**: Browses the web to find relevant information
- **FileSurferAgent**: Processes and analyzes files

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nonprofit_grant_writer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the `.env.example` file to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

## Configuration

You'll need to configure the following services:

1. **Azure OpenAI**: Obtain API keys and endpoints from the Azure Portal
2. **Bing Search API**: Get API keys from Microsoft Azure (for research capabilities)
3. **Qdrant** (optional): Set up a Qdrant instance for vector storage

Fill in these credentials in your `.env` file.

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Fill in the form with your nonprofit's information and the grant URL
4. Wait for the agents to generate your grant application
5. Review and edit the content on the review page
6. Download the final document as a DOCX file

## API Endpoints

- `POST /api/generate-grant`: Initiates the grant generation process
- `GET /api/get-grant-status`: Checks the status of the generation process
- `POST /api/save-grant`: Saves the edited grant as a DOCX file

## Directory Structure

```
nonprofit_grant_writer/
├── app.py                         # Main application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── backend/                       # Backend code
│   ├── agents/                    # Agent implementations
│   │   ├── orchestrator.py        # Main orchestrator agent
│   │   ├── researcher.py          # Research agent
│   │   ├── writer.py              # Content writing agent
│   │   ├── nonprofit_grounding.py # Mission alignment agent
│   │   ├── quality_checker.py     # Quality evaluation agent
│   │   ├── scraper.py             # Website scraping agent
│   │   ├── web_surfer.py          # Web browsing agent
│   │   └── file_surfer.py         # File processing agent
│   ├── tools/                     # Tools used by agents
│   │   └── qdrant_tool.py         # Vector database tool
│   ├── models/                    # Data models
│   └── utils/                     # Utility functions
│       └── docx_generator.py      # DOCX file generation
├── frontend/                      # Frontend code
│   ├── static/                    # Static assets
│   │   ├── css/                   # CSS styles
│   │   │   └── styles.css         # Main stylesheet
│   │   └── js/                    # JavaScript files
│   │       ├── main.js            # Main page script
│   │       └── review.js          # Review page script
│   └── templates/                 # HTML templates
│       ├── index.html             # Main form page
│       └── review.html            # Content review page
└── data/                          # Data storage
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 