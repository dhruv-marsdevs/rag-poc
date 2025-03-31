# RAG API with FastAPI and MongoDB

This project implements a production-ready Retrieval Augmented Generation (RAG) system using FastAPI and MongoDB Atlas Vector Search. It allows users to upload PDF and Word documents, which are processed, chunked, and indexed in a vector database. Users can then ask questions, and the system will retrieve relevant documents to generate accurate answers with source citations.

## Features

- Document upload (PDF and DOCX formats)
- Automatic document processing and indexing
- Question answering with source citations
- REST API interface with OpenAPI documentation
- Authentication with JWT tokens and API keys
- Containerized deployment with Docker
- Logging, error handling, and monitoring
- Multi-tenancy support

## Project Structure

The project follows a clean architecture pattern with clear separation of concerns:

```
app/
├── api/
│   ├── deps.py          # Dependency injection
│   └── v1/              # API version 1
│       ├── api.py       # API router
│       └── endpoints/   # API endpoints
├── core/                # Core configuration
│   ├── config.py        # Settings
│   ├── logging.py       # Logging configuration
│   └── security.py      # Authentication and security
├── schemas/             # Pydantic models
│   ├── document.py      # Document schemas
│   └── user.py          # User schemas
├── services/            # Business logic
│   ├── document_service.py    # Document processing
│   ├── rag_service.py         # RAG implementation
│   └── vector_store_service.py # Vector store interactions
└── main.py              # Application entry point
```

## Setup

### Local Development

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install vector store dependencies:
   ```bash
   python fix_dependencies.py
   ```
5. Create a `.env` file based on `.env.example` and add your OpenAI API key
6. Start MongoDB (or use a cloud-hosted instance)
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```
7. Run the application:
   ```bash
   python run.py
   ```

### Docker Deployment

1. Clone this repository
2. Create a `.env` file based on `.env.example`
3. Build and run using Docker Compose:
   ```bash
   docker-compose up -d
   ```

The API will be available at http://localhost:8000, and the Swagger documentation at http://localhost:8000/docs.

## API Endpoints

### Authentication

- `POST /api/v1/auth/login/access-token` - Get a JWT token
- `POST /api/v1/auth/api-keys` - Create an API key

### Documents

- `POST /api/v1/documents/upload` - Upload PDF or Word documents
- `GET /api/v1/documents` - List all uploaded documents
- `DELETE /api/v1/documents/{document_id}` - Delete a document

### Query

- `POST /api/v1/query` - Ask a question about the uploaded documents

## Authentication

The API supports two authentication methods:

1. **JWT Tokens**: Standard OAuth2 token-based authentication
2. **API Keys**: Custom API keys sent via the `X-API-Key` header

For development, you can use the following credentials:
- Username: `admin@example.com`
- Password: `password`

## Data Storage

- Documents are stored in the `./data/documents` directory
- MongoDB is used for vector database storage
- In a production environment, consider using MongoDB Atlas or another managed MongoDB service

## Production Deployment

For production deployment, consider:

1. Using a reverse proxy like Nginx
2. Setting up proper TLS/SSL
3. Using managed database services like MongoDB Atlas
4. Implementing proper monitoring and alerting
5. Setting up CI/CD pipelines

## Troubleshooting

### Vector Store Issues

If you encounter issues with the vector store:

1. **Empty responses**: If you get empty responses when querying, make sure you've uploaded at least one document first.

2. **"Vector store not available" errors**:
   - Check that MongoDB is running and accessible
   - Verify the MongoDB connection URI in your `.env` file
   - Make sure you have the correct permissions to access the MongoDB instance

3. **Check system status**:
   ```
   curl -X GET "http://localhost:8000/api/v1/system/status" -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Debug vector store**:
   ```
   python debug_vector.py
   ```

5. **Reset MongoDB collection**:
   ```bash
   # Using MongoDB shell
   mongo
   use rag_db
   db.document_chunks.drop()
   ```

### LangChain Deprecation Warnings

You may see warnings about deprecated LangChain imports. These are informational and don't affect functionality. We've updated the code to use the latest recommended imports.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 