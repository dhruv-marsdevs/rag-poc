#!/usr/bin/env python3
"""
This script removes all Chroma DB related files and directories
after migrating to MongoDB.
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_chroma_files():
    """Remove all Chroma DB related files and directories"""
    
    # List of directories to check and remove if they exist
    chroma_dirs = [
        "./data/chroma",
        "./data/chromadb",
    ]
    
    removed_count = 0
    
    for dir_path in chroma_dirs:
        if os.path.exists(dir_path):
            try:
                logger.info(f"Removing Chroma directory: {dir_path}")
                shutil.rmtree(dir_path)
                removed_count += 1
            except Exception as e:
                logger.error(f"Error removing {dir_path}: {str(e)}")
    
    if removed_count > 0:
        logger.info(f"Successfully removed {removed_count} Chroma directories")
    else:
        logger.info("No Chroma directories found to remove")

if __name__ == "__main__":
    logger.info("Starting Chroma DB cleanup")
    cleanup_chroma_files()
    logger.info("Chroma DB cleanup completed") 