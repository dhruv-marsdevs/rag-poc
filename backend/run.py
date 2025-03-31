import uvicorn
import os
from dotenv import load_dotenv
from app.core.config import get_settings

# Load environment variables
load_dotenv()

# Get application settings
settings = get_settings()

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
