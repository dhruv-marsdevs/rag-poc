import sys
import logging
import traceback
from app.services.vector_store_service import get_vector_store, query_vectorstore

# Configure logging to show more details
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handler to write to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    # Try to get the vector store
    print("\n=== INITIALIZING VECTOR STORE ===")
    vector_store = get_vector_store()
    print(f"Vector store: {vector_store}")

    # Check collection info
    print("\n=== CHECKING COLLECTION INFO ===")
    if hasattr(vector_store, "collection") and vector_store.collection:
        try:
            collection_count = vector_store.collection.count_documents({})
            print(f"Collection count: {collection_count}")

            # Get collection info
            collection_name = vector_store.collection.name
            print(f"Collection name: {collection_name}")

            # Check embedding function
            print(f"Embedding function: {vector_store.embedding}")
        except Exception as e:
            print(f"Error getting collection info: {str(e)}")
    else:
        print("Vector store has no collection attribute")

    # Try to query it
    print("\n=== QUERYING VECTOR STORE ===")
    results = query_vectorstore("test query")
    print(f"Query results: {results}")

    # Try manually querying
    print("\n=== MANUALLY QUERYING VECTOR STORE ===")
    if hasattr(vector_store, "collection") and vector_store.collection:
        try:
            print("Getting first document from MongoDB")
            first_doc = vector_store.collection.find_one()
            if first_doc:
                print(f"First document: {first_doc}")
            else:
                print("No documents found in collection")
        except Exception as e:
            print(f"Error manually querying: {str(e)}")

except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()
