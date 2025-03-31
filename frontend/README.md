# RAG System Frontend

A modern React-based frontend for the Retrieval Augmented Generation (RAG) system. Built with Next.js and Ant Design, this application provides an intuitive interface for document management, querying, and user profile management.

## Features

- **Document Management**
  - Upload PDF and DOCX documents
  - Website scraping for content extraction
  - Document library with file management

- **Query Interface**
  - Natural language querying of documents
  - AI-generated answers with source attribution
  - Interactive chat-like experience

- **User Management**
  - User authentication with JWT
  - Profile management
  - Password change functionality
  
- **Dashboard**
  - System statistics and visualizations
  - Document and query metrics
  - Real-time data from the backend

## Technology Stack

- **Next.js 14**: React framework with App Router
- **Ant Design 5**: UI component library
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests
- **React Context**: State management
- **React Hooks**: Custom hooks for shared functionality

## Project Structure

```
frontend/
├── public/                # Static assets
├── src/
│   ├── api/               # API service functions
│   │   ├── auth.js        # Authentication API
│   │   ├── documents.js   # Document management API
│   │   ├── query.js       # Query API
│   │   └── user.js        # User management API
│   ├── app/               # Next.js pages
│   │   ├── documents/     # Document management page
│   │   ├── login/         # Login page
│   │   ├── profile/       # User profile page
│   │   ├── query/         # Query interface page
│   │   └── register/      # User registration page
│   ├── components/        # Reusable React components
│   ├── context/           # React context providers
│   ├── hooks/             # Custom React hooks
│   └── layouts/           # Page layout components
└── package.json           # Project dependencies
```

## Setup and Installation

### Prerequisites

- Node.js 18.x or later
- Backend API running (see backend README.md)

### Installation Steps

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The application will be available at http://localhost:3000

## Key Features

### Document Management

The document management page allows users to:
- Upload PDF and DOCX files for processing
- Scrape websites to extract and process their content
- View all uploaded documents in a sortable table
- Delete documents from the system

### Query Interface

The query page provides:
- A chat-like interface for asking questions about your documents
- AI-generated answers based on the content of your documents
- Source citations showing where information was found
- A seamless user experience for knowledge retrieval

### User Management

User management features include:
- User registration and login
- Profile viewing and editing
- Password changing
- Session management

### Dashboard

The dashboard displays:
- Total document count
- Number of queries performed today
- Active user count
- Average response time
- Document type distribution

## Development

### Code Organization

- **API Module**: Contains all API calls organized by domain
- **Components**: Reusable UI components with clear responsibilities
- **Context**: Global state management for authentication and app-wide state
- **Hooks**: Custom hooks for shared functionality across components

### Adding New Features

1. Create API service functions in the appropriate file in `/src/api/`
2. Add UI components in `/src/components/`
3. Create or update pages in `/src/app/`
4. Update context providers if needed for state management

## Deployment

### Build for Production

```bash
npm run build
# or
yarn build
```

### Deploy on Vercel

The easiest way to deploy the application is using Vercel:

1. Push your code to a GitHub repository
2. Import the project in Vercel
3. Configure environment variables
4. Deploy

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Ensure the backend API is running
   - Check API URL configuration in the frontend

2. **Authentication Problems**
   - Clear browser cookies/local storage
   - Verify credentials are correct

3. **Upload Failures**
   - Check file size and format
   - Verify backend storage configuration

## License

This project is licensed under the MIT License.
