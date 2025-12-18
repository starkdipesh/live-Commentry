
import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Set up paths
sys.path.append(os.getcwd())

from src.core.gameplay_commentator_enhanced import EnhancedGameplayCommentator

class TestEnhancedCommentator(unittest.TestCase):
    
    @patch('requests.get')
    def test_model_fallback(self, mock_get):
        # Simulate Ollama response with only llava:latest
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llava:latest"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Initialize commentator (it calls _check_ollama_status in __init__)
        commentator = EnhancedGameplayCommentator()
        
        # Check if it fell back to llava:latest
        print(f"DEBUG: Selected model: {commentator.model_name}")
        self.assertEqual(commentator.model_name, "llava:latest")
        print("✅ Fallback logic verified!")

    @patch('requests.post')
    @patch('requests.get')
    def test_generate_commentary_safety(self, mock_get, mock_post):
        # Setup get mock
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "llava:latest"}]}
        
        # Setup post mock for 404/Error
        mock_post_response = MagicMock()
        mock_post_response.status_code = 404
        mock_post_response.text = "Model not found"
        mock_post.return_value = mock_post_response
        
        commentator = EnhancedGameplayCommentator()
        
        # Create a blank image for testing
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Should NOT crash, should return fallback
        commentary = commentator.generate_commentary_enhanced(img)
        print(f"DEBUG: Got commentary even on error: {commentary}")
        self.assertIsNotNone(commentary)
        print("✅ Error handling verified!")

if __name__ == '__main__':
    unittest.main()
