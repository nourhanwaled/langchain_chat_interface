import os
import shutil
from ..config import VECTOR_STORE_PATH

def export_vector_store(output_path: str = None) -> str:
    """
    Export the vector store as a ZIP file.
    
    Args:
        output_path: Optional path where to save the ZIP file.
                    If not provided, saves in the same directory as VECTOR_STORE_PATH.
    
    Returns:
        str: Path to the created ZIP file
    """
    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError("Vector store directory not found. Please create the vector store first.")

    # If no output path provided, use the same directory as VECTOR_STORE_PATH
    if output_path is None:
        output_path = os.path.join(os.path.dirname(VECTOR_STORE_PATH), "vector_index_storage.zip")
    
    # Create the ZIP file
    try:
        shutil.make_archive(
            base_name=os.path.splitext(output_path)[0],  # Remove .zip extension if present
            format="zip",
            root_dir=VECTOR_STORE_PATH
        )
        return output_path
    except Exception as e:
        raise Exception(f"Failed to create ZIP file: {str(e)}")

def import_vector_store(zip_path: str) -> None:
    """
    Import a vector store from a ZIP file.
    
    Args:
        zip_path: Path to the ZIP file containing the vector store
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file not found at: {zip_path}")

    # Remove existing vector store if it exists
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)

    # Extract the ZIP file
    try:
        shutil.unpack_archive(zip_path, VECTOR_STORE_PATH, "zip")
    except Exception as e:
        raise Exception(f"Failed to extract ZIP file: {str(e)}") 