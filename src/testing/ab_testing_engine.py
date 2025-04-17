from typing import Dict, Any, List
import numpy as np
from scipy import stats
import pandas as pd
from datetime import datetime
import uuid
from enum import Enum

class TestStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    SCHEDULED = "scheduled"

class ABTestingEngine:
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
        self.user_assignments = {}
        
    async def create_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new A/B test"""
        test_id = str(uuid.uuid4())
        test = {
            "id": test_id,
            "name": test_config["name"],
            "description": test_config["description"],
            "variants": test_config["variants"],
            "metrics": test_config["metrics"],
            "start_time": datetime.now(),
            "status": TestStatus.ACTIVE,
            "sample_size": test_config.get("sample_size", 0),
            "confidence_level": test_config.get("confidence_level", 0.95),
            "data": {variant: [] for variant in test_config["variants"]}
        }
        
        self.active_tests[test_id] = test
        return {"status": "success", "test_id": test_id}

    async def assign_user_to_variant(self, user_id: str, test_id: str) -> Dict[str, Any]:
        """Assign a user to a test variant"""
        if test_id not in self.active_tests:
            return {"status": "error", "message": "Test not found"}
            
        if user_id in self.user_assignments. 