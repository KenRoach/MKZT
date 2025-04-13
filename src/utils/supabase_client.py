import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create a Supabase client instance.
        Uses GitHub authentication if available.
        """
        if cls._instance is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_API_KEY")
            
            if not url or not key:
                raise ValueError("Missing Supabase credentials in .env file")
            
            cls._instance = create_client(url, key)
            
            # If GitHub token is available, sign in with GitHub
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                try:
                    cls._instance.auth.sign_in_with_github(github_token)
                except Exception as e:
                    print(f"Warning: Failed to authenticate with GitHub: {e}")
        
        return cls._instance

# Create a singleton instance
supabase = SupabaseClient.get_client() 