# RAG System Backend

This is the backend service for a Retrieval Augmented Generation (RAG) system built with FastAPI, SQLAlchemy, and Chroma Vector DB. It provides API endpoints for document management, query processing, and user authentication.

## Features

- **Document Management**
  - Upload PDF and DOCX documents
  - Process and chunk documents for vector storage
  - **New!** Website scraping and content extraction
  - Delete documents and their vector embeddings

- **Query Processing**
  - Semantic search across all documents
  - Relevant context retrieval for LLM-based answers
  - Source attribution for transparent responses

- **User Management**
  - JWT-based authentication
  - User registration and profile management
  - Secure password handling
  - Password change functionality

- **System Monitoring**
  - Vector store status endpoint
  - System statistics for dashboard
  - Document and query metrics

## Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Chroma DB**: Vector database for document embeddings
- **LangChain**: Framework for building LLM applications
- **Beautiful Soup**: Library for web scraping
- **Sentence Transformers**: For generating embeddings (optional OpenAI embeddings)
- **PyPDF & python-docx**: For document processing

## Project Structure

```
backend/
├── app/
│   ├── api/                # API routes and dependencies
│   │   └── v1/
│   │       └── endpoints/  # API endpoint implementations
│   ├── core/               # Core configuration and settings
│   ├── db/                 # Database connections and models
│   ├── middlewares/        # Request/response middlewares
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas for validation
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── data/                   # Data storage (documents, vector DB)
├── tests/                  # Test suite
├── .env                    # Environment variables (create from .env.example)
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Setup and Installation

### Prerequisites

- Python 3.9+
- MongoDB (optional, for advanced features)
- OpenAI API key (optional, for OpenAI embeddings)

### Installation Steps

1. **Clone the repository**

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key (optional)
   - Configure other settings as needed

5. **Create necessary directories**
   ```bash
   mkdir -p data/documents
   ```

6. **Run the application**
   ```bash
   python run.py
   ```
   The API will be available at http://localhost:8000

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/access-token` - Get JWT token
- `POST /api/v1/auth/api-keys` - Create API key

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/me/password` - Change password

### Documents
- `POST /api/v1/documents/upload` - Upload documents
- `POST /api/v1/documents/scrape-website` - Scrape website content
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{document_id}` - Delete a document

### Query
- `POST /api/v1/query` - Query documents and get AI-generated answers

### System
- `GET /api/v1/system/status` - Get system status
- `GET /api/v1/system/stats` - Get system statistics

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app tests
isort app tests
flake8 app tests
```

## Troubleshooting

### Common Issues

1. **Vector store initialization errors**
   - Ensure the `EMBEDDING_MODEL` in your `.env` file is correct
   - Check that you have sufficient permissions for the data directory

2. **Document processing errors**
   - Make sure the document files are not corrupted
   - Verify you have the correct dependencies for PDF and DOCX processing

3. **Website scraping issues**
   - Some websites may block scraping attempts
   - Check the website's robots.txt file for restrictions

## License

This project is licensed under the MIT License. 