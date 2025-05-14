"""
License validator service for the Clary AI API.

This module provides services for validating API keys and container licenses.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import requests

from app.core.config import settings


class LicenseValidator:
    """License validator service."""
    
    def __init__(self):
        """Initialize the license validator."""
        self.cache_file = os.path.join(settings.MODEL_PATH, ".license_cache")
        self.last_check = 0
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """
        Load the license cache from disk.
        
        Returns:
            Dict: The license cache.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"valid_until": 0, "container_id": "", "key_hash": ""}
    
    def _save_cache(self) -> None:
        """Save the license cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f)
        except Exception:
            pass
    
    def validate(self, api_key: str, container_id: str) -> Tuple[bool, str]:
        """
        Validate the license with the license server.
        
        Args:
            api_key: The API key to validate.
            container_id: The unique ID of this container.
            
        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the license is valid,
                and a string with an error message if it's not valid.
        """
        # If license validation is disabled, return valid
        if not settings.LICENSE_VALIDATION_ENABLED:
            return True, ""
        
        # Hash the API key for secure storage and transmission
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Check if we need to validate with the server
        current_time = int(time.time())
        cache_valid = (
            self.cache["valid_until"] > current_time and
            self.cache["container_id"] == container_id and
            self.cache["key_hash"] == key_hash
        )
        
        # If the cache is valid and we've checked recently, return the cached result
        if cache_valid and (current_time - self.last_check) < settings.LICENSE_CHECK_INTERVAL * 3600:
            return True, ""
        
        # Try to validate with the license server
        try:
            response = requests.post(
                settings.LICENSE_SERVER_URL,
                json={
                    "key_hash": key_hash,
                    "container_id": container_id,
                    "timestamp": current_time
                },
                timeout=5
            )
            
            self.last_check = current_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid", False):
                    # Update cache
                    self.cache = {
                        "valid_until": current_time + (settings.LICENSE_CHECK_INTERVAL * 3600),
                        "container_id": container_id,
                        "key_hash": key_hash
                    }
                    self._save_cache()
                    return True, ""
                else:
                    return False, data.get("message", "License validation failed")
            else:
                # If we can't reach the server but have a valid cache, use it
                if cache_valid:
                    return True, ""
                return False, f"License server error: {response.status_code}"
                
        except Exception as e:
            # If we can't reach the server but have a valid cache, use it
            if cache_valid:
                return True, ""
            return False, f"License validation error: {str(e)}"
    
    def get_license_info(self, api_key: str) -> Dict:
        """
        Get information about the license.
        
        Args:
            api_key: The API key to check.
            
        Returns:
            Dict: Information about the license.
        """
        # Hash the API key for secure transmission
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            response = requests.get(
                f"{settings.LICENSE_SERVER_URL}/info",
                params={"key_hash": key_hash},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"License server error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"License info error: {str(e)}"}


# Create global license validator instance
license_validator = LicenseValidator()
