from typing import Dict, Any
import asyncio
from deployment_orchestrator import AutomatedDeployment
from test_orchestrator import AutomatedTesting
from monitoring_orchestrator import AutomatedMonitoring
from scaling_orchestrator import AutomatedScaling
from backup_orchestrator import AutomatedBackup

class AutomationOrchestrator:
    def __init__(self):
        self.deployment = AutomatedDeployment()
        self.testing = AutomatedTesting()
        self.monitoring = AutomatedMonitoring()
        self.scaling = AutomatedScaling()
        self.backup = AutomatedBackup()
        
    async def start_automation(self):
        """Start all automation systems"""
        try:
            # Start all automation systems
            await asyncio.gather(
                self.monitoring.start_automated_monitoring(),
                self.scaling.start_automated_scaling(),
                self.backup.start_automated_backup()
            )
            
        except Exception as e:
            logging.error(f"Automation failed: {str(e)}")
            raise
            
    async def automated_deployment_pipeline(self, 
                                         version: str,
                                         environment: str) -> Dict[str, Any]:
        """Run automated deployment pipeline"""
        try:
            # Run tests
            test_results = await self.testing.run_automated_tests()
            if not test_results['success']:
                raise Exception("Tests failed")
                
            # Deploy
            deployment_result = await self.deployment.automated_deployment(
                version,
                environment
            )
            
            return {
                "status": "success",
                "test_results": test_results,
                "deployment": deployment_result
            }
            
        except Exception as e:
            logging.error(f"Deployment pipeline failed: {str(e)}")
            raise

# Usage
if __name__ == "__main__":
    orchestrator = AutomationOrchestrator()
    
    # Start automation
    asyncio.run(orchestrator.start_automation())
    
    # Run deployment
    asyncio.run(orchestrator.automated_deployment_pipeline(
        version="1.0.0",
        environment="production"
    )) 