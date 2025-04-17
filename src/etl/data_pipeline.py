from typing import Dict, Any, List, Optional
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from dataclasses import dataclass

@dataclass
class ETLConfig:
    source_config: Dict[str, Any]
    transform_config: Dict[str, Any]
    load_config: Dict[str, Any]
    schedule: str

class DataPipeline:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.pipeline_options = PipelineOptions()
        
    def build_pipeline(self) -> beam.Pipeline:
        """Build ETL pipeline"""
        pipeline = beam.Pipeline(options=self.pipeline_options)
        
        # Read from sources
        orders = pipeline | "Read Orders" >> beam.io.Read(
            self
        )
        
        return pipeline 