from functools import wraps
import requests
import os
from datetime import datetime
from .log import log_error, log_info
from typing import Dict, Any

class DjangoAuthTokenManager:
    _instance = None
    _token = None
    _user_info = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DjangoAuthTokenManager, cls).__new__(cls)
        return cls._instance

    def get_auth_info(self) -> Dict[str, Any]:
        if not self._token:
            self._login()
        return {
            'token': self._token,
            'user_info': self._user_info
        }
    
    def _login(self) -> None:
        try:
            base_url = os.getenv("BASE_API_URL")
            email = os.getenv('USER_EMAIL')
            password = os.getenv('USER_PASSWORD')
            
            login_url = f"{base_url}/api/v1/login/"
            login_data = {
                "email": email,
                "password": password
            }
            
            login_response = requests.post(login_url, json=login_data)
            if login_response.status_code != 200:
                raise Exception(f"Login failed=========: {login_response}")
            
            response_data = login_response.json()
            self._token = response_data.get('token')
            
            self._user_info = {
                'user_id': response_data.get('user_id'),
                'email': response_data.get('email'),
                'role': response_data.get('role')
            }
            
            if not self._token:
                raise Exception("No token received in login response")
                
            log_info("Successfully logged in and received new auth token")
            
        except Exception as e:
            log_error(f"Error during login: {str(e)}")
            raise

    def clear_token(self) -> None:
        self._token = None
        self._user_info = None

def with_django_auth(func):
    """Decorator to automatically handle Django authentication token in API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token_manager = DjangoAuthTokenManager()
            auth_info = token_manager.get_auth_info()
            
            kwargs['headers'] = {
                'Authorization': f"Token {auth_info['token']}",
                **(kwargs.get('headers', {}))
            }
            
            response = func(*args, **kwargs)
            
            if isinstance(response, requests.Response) and response.status_code == 401:
                token_manager.clear_token()
                auth_info = token_manager.get_auth_info()
                kwargs['headers']['Authorization'] = f"Token {auth_info['token']}"
                response = func(*args, **kwargs)
                
            return response
            
        except Exception as e:
            log_error(f"Error in auth wrapper: {str(e)}")
            raise
            
    return wrapper
