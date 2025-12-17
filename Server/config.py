from pydantic_settings import BaseSettings
from typing import Optional
import json
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    DATABASE_URL: str
    DEBUG: bool = False
    SECRET_KEY: Optional[str] = None
    ESP32_IP: str = "192.168.1.100"
    ESP32_PORT: int = 80
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None  # Can be JSON string or file path
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Handle Google Cloud credentials
_google_credentials_file = None

def get_google_credentials_path() -> Optional[str]:
    """Get path to Google Cloud credentials file
    
    Handles both JSON string (from .env) and file path formats.
    If JSON string, creates temporary file. If file path, uses directly.
    """
    global _google_credentials_file
    
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        return None
    
    # If it's already a file path, use it
    if os.path.isfile(settings.GOOGLE_APPLICATION_CREDENTIALS):
        logger.info(f"Using Google Cloud credentials from file: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        return settings.GOOGLE_APPLICATION_CREDENTIALS
    
    # Try to parse as JSON string
    try:
        # Handle both JSON string and escaped JSON string
        creds_str = settings.GOOGLE_APPLICATION_CREDENTIALS.strip()
        
        # If it starts with {, it's likely a JSON string (not a file path)
        if creds_str.startswith('{'):
            # Try multiple parsing strategies
            creds_json = None
            
            # Strategy 1: Try to parse directly
            try:
                creds_json = json.loads(creds_str)
            except json.JSONDecodeError:
                # Strategy 2: Handle escaped newlines
                # In .env, \\n is stored as literal backslash+n (two chars)
                # JSON needs \n (escaped newline, two chars in Python string: backslash + n)
                # So we need: \\\\n (4 backslashes + n in Python) -> \\n (2 backslashes + n in Python)
                try:
                    import re
                    # Replace \\\\n (literal backslash+backslash+n) with \\n (JSON escape sequence)
                    # This converts the literal backslash+n to the JSON escape sequence
                    fixed_str = re.sub(r'\\\\n', r'\\n', creds_str)
                    # Also handle \\\\" -> \\"
                    fixed_str = re.sub(r'\\\\"', r'\\"', fixed_str)
                    creds_json = json.loads(fixed_str)
                except json.JSONDecodeError as e2:
                    # Strategy 3: Try using raw string replacement
                    try:
                        # More direct: replace literal \\n with JSON escape \n
                        fixed_str = creds_str.replace('\\\\n', '\\n')
                        fixed_str = fixed_str.replace('\\\\"', '\\"')
                        creds_json = json.loads(fixed_str)
                    except Exception as e3:
                        logger.error(f"All JSON parsing strategies failed. Strategy 2: {str(e2)}, Strategy 3: {str(e3)}")
                        raise json.JSONDecodeError(f"Could not parse JSON. Last error: {str(e3)}", creds_str, 0)
            
            if creds_json:
                # Create temporary file if not already created
                if _google_credentials_file is None:
                    fd, _google_credentials_file = tempfile.mkstemp(suffix='.json', prefix='gcp_creds_')
                    os.close(fd)
                    
                    # Fix private_key field - ensure newlines are properly handled
                    # After JSON parsing, \n escape sequences should become actual newlines
                    # But sometimes they remain as literal \n (backslash+n), which breaks PEM parsing
                    if 'private_key' in creds_json and isinstance(creds_json['private_key'], str):
                        # Always replace literal \n (backslash+n) with actual newline
                        # This ensures PEM format is correct regardless of how JSON was parsed
                        creds_json['private_key'] = creds_json['private_key'].replace('\\n', '\n')
                        # Also handle any remaining literal backslash+n patterns
                        import re
                        creds_json['private_key'] = re.sub(r'\\+n', '\n', creds_json['private_key'])
                    
                    # Write JSON to temporary file
                    # json.dump will properly escape newlines in the JSON output
                    with open(_google_credentials_file, 'w', encoding='utf-8') as f:
                        json.dump(creds_json, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Google Cloud credentials saved to temporary file: {_google_credentials_file}")
                
                return _google_credentials_file
        else:
            # Not a JSON string, treat as file path
            logger.warning(f"GOOGLE_APPLICATION_CREDENTIALS does not start with {{, treating as file path")
            return settings.GOOGLE_APPLICATION_CREDENTIALS
        
    except json.JSONDecodeError:
        # Not valid JSON, assume it's a file path (even if file doesn't exist yet)
        logger.warning(f"GOOGLE_APPLICATION_CREDENTIALS is not valid JSON, treating as file path: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        return settings.GOOGLE_APPLICATION_CREDENTIALS
    except Exception as e:
        logger.error(f"Error processing Google Cloud credentials: {str(e)}")
        return None

