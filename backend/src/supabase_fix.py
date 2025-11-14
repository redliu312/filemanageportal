"""
Fix for Supabase client header encoding issues
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def create_fixed_supabase_client(url: str, key: str):
    """
    Create a Supabase client with fixed headers to prevent boolean encoding errors
    """
    from supabase import create_client, Client
    
    # Ensure URL and key are strings
    url = str(url) if url else ""
    key = str(key) if key else ""
    
    logger.debug(f"Creating Supabase client with URL: {url[:50]}...")
    
    # Create the client
    client = create_client(url, key)
    
    # Fix headers in the client and its sub-clients
    def fix_headers(obj: Any, path: str = ""):
        """Recursively fix headers in an object"""
        if hasattr(obj, '_headers'):
            logger.debug(f"Checking headers at {path}")
            headers = obj._headers
            if isinstance(headers, dict):
                for k, v in list(headers.items()):
                    if isinstance(v, bool):
                        logger.info(f"FOUND BOOLEAN HEADER at {path}.{k}: {v} -> converting to {str(v).lower()}")
                        logger.info(f"Boolean header details - key: '{k}', value: {v}, type: {type(v)}")
                        headers[k] = str(v).lower()
                    elif v is None:
                        logger.info(f"Fixed None header at {path}.{k} -> empty string")
                        headers[k] = ""
                    elif not isinstance(v, str):
                        logger.info(f"Fixed non-string header at {path}.{k}: {v} ({type(v)}) -> {str(v)}")
                        headers[k] = str(v)
        
        # Check nested clients
        if hasattr(obj, 'storage'):
            fix_headers(obj.storage, f"{path}.storage")
        if hasattr(obj, '_client'):
            fix_headers(obj._client, f"{path}._client")
        if hasattr(obj, 'auth'):
            fix_headers(obj.auth, f"{path}.auth")
    
    # Apply fixes
    fix_headers(client, "client")
    
    # Monkey patch the storage client's request method to ensure headers are always strings
    if hasattr(client, 'storage') and hasattr(client.storage, '_client'):
        storage_client = client.storage._client
        original_request = storage_client.request
        
        def safe_request(method, url, **kwargs):
            # Ensure all headers are strings
            if 'headers' in kwargs and isinstance(kwargs['headers'], dict):
                safe_headers = {}
                for k, v in kwargs['headers'].items():
                    if isinstance(v, bool):
                        #TODO: this is for vercel env got error: FOUND BOOLEAN HEADER in request - key: 'upsert', value: False
                        logger.info(f"FOUND BOOLEAN HEADER in request - key: '{k}', value: {v}")
                        safe_headers[k] = str(v).lower()
                    elif v is None:
                        logger.info(f"Found None header in request - key: '{k}'")
                        safe_headers[k] = ""
                    elif not isinstance(v, str):
                        logger.info(f"Found non-string header in request - key: '{k}', value: {v}, type: {type(v)}")
                        safe_headers[k] = str(v)
                    else:
                        safe_headers[k] = v
                kwargs['headers'] = safe_headers
            
            return original_request(method, url, **kwargs)
        
        storage_client.request = safe_request
        logger.debug("Patched storage client request method")
    
    return client