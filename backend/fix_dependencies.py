#!/usr/bin/env python
import sys
import subprocess
import logging
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_and_install(package_name, import_name=None):
    """Check if a package is installed and install it if not."""
    if import_name is None:
        import_name = package_name

    try:
        # Try to import the package
        if importlib.util.find_spec(import_name) is None:
            logger.info(f"Installing {package_name}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
            logger.info(f"Successfully installed {package_name}")
        else:
            logger.info(f"{package_name} is already installed.")
        return True
    except Exception as e:
        logger.error(f"Failed to install {package_name}: {str(e)}")
        return False


def main():
    """Install all required dependencies for the vector store."""
    logger.info("Checking and installing required dependencies...")

    # Core dependencies
    packages = [
        "langchain-huggingface",
        "langchain-chroma",
        "sentence-transformers",
        "chromadb>=0.4.18",
    ]

    # Install each package
    success = True
    for package in packages:
        if not check_and_install(package):
            success = False

    if success:
        logger.info("All dependencies have been successfully installed!")
        logger.info("You can now run the application with: python run.py")
    else:
        logger.error(
            "Some dependencies could not be installed. Please check the logs and try again."
        )


if __name__ == "__main__":
    main()
