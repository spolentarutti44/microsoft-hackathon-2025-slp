# Nonprofit Grant Application Builder

Nonprofit Grant Application Builder is a multi-agent AI system that helps nonprofit organizations create high-quality grant applications. 

Users input their organization details and a grant URL, and the application uses Microsoft Semantic Kernel agents with Azure OpenAI to draft the content.

## Architecture

This project consists of two main components:

1. **Backend API (Quart)**  
   - Provides JSON endpoints for generating and retrieving grant content.  
   - Uses Semantic Kernel orchestrator agent to coordinate specialized agents (Scraper, Researcher, Writer, QualityChecker, etc.).  
   - Stores intermediate results in `data/temp_result.json`.

2. **Web UI (Django)**  
   - Offers a user-friendly interface for input and review.  
   - Static assets and templates are packaged in the `ui` Django app.  
   - Runs as a Django project in the `webui` directory.

## Features

- Input nonprofit name, mission, website, and grant URL.  
- Background processing of grant generation.  
- Rich text review with Quill.js editors for each section (Overview, Executive Summary, etc.).  
- Budget table editing with dynamic item addition/removal.  
- Export final application as a DOCX document.

## Tech Stack

- Python 3.9+  
- Quart & quart-cors  
- Django 4.2  
- Microsoft Semantic Kernel  
- Azure OpenAI  
- Qdrant (vector DB)  
- Bootstrap 5 & Quill.js  

## Getting Started

### Prerequisites

- Python 3.9 or higher  
- pip & virtualenv  

### Installation

```bash
git clone <repository-url>
cd nonprofit_grant_writer_dj
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root (next to `app.py`) and set the following variables:

```env
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
AZURE_OPENAI_KEY=<your-azure-openai-key>
FLASK_SECRET_KEY=<your-secret-key>
FLASK_DEBUG=true
# Add any other keys (Bing API, Qdrant, etc.)
```

### Running

1. **Start the Backend API**  
   ```bash
   python app.py
   ```  
   The API listens on `http://127.0.0.1:5000`.

2. **Start the Web UI**  
   ```bash
   cd webui
   python manage.py runserver 8000
   ```  
   The UI is available at `http://127.0.0.1:8000`.

3. **Use the Application**  
   - Open `http://127.0.0.1:8000` in your browser.  
   - Fill in your nonprofit details and grant URL on the home page.  
   - Click **Generate Grant Application** and wait for processing.  
   - After redirect, review and edit each section.  
   - Click **Save as DOCX** to download your finalized application.

## Project Structure

```
nonprofit_grant_writer_dj/
├── app.py                 # Quart backend entrypoint
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
├── ui/                    # Django app for UI (templates & static)
├── webui/                 # Django project for UI server
│   ├── webui/             # Django settings & wsgi
│   └── manage.py          # Django management script
├── backend/               # AI agent implementations
└── data/                  # Temporary result storage
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 