"""BigQuery service for database operations"""

from google.cloud import bigquery
from typing import List, Dict, Any, Optional
from app.config import settings
import json

class BigQueryService:
    """Service for BigQuery operations"""

    def __init__(self):
        self.client = bigquery.Client(project=settings.PROJECT_ID)
        self.dataset_id = settings.DATASET_ID

    def query(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dicts"""
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = params

        query_job = self.client.query(sql, job_config=job_config)
        results = query_job.result()

        return [dict(row) for row in results]

    def insert_rows(self, table_id: str, rows: List[Dict[str, Any]]) -> None:
        """
        Insert rows into table using batch mode (load job) instead of streaming.

        This avoids the streaming buffer limitation where UPDATE/DELETE
        cannot be performed on recently inserted rows.

        In development, we use batch inserts via load_table_from_json.
        In production, you may want to use streaming for lower latency.
        """
        full_table_id = f"{settings.PROJECT_ID}.{self.dataset_id}.{table_id}"
        table = self.client.get_table(full_table_id)

        # Use batch insert (load job) instead of streaming insert
        # This allows immediate UPDATE/DELETE operations
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        # Convert rows to NDJSON format
        ndjson_data = "\n".join([json.dumps(row) for row in rows])

        # Load data as a job (batch mode)
        job = self.client.load_table_from_json(
            rows,
            table,
            job_config=job_config
        )

        # Wait for job to complete
        job.result()

        if job.errors:
            raise Exception(f"BigQuery insert errors: {job.errors}")

    def execute(self, sql: str, params: Optional[List] = None) -> None:
        """
        Execute SQL without returning results (for UPDATE, DELETE, etc.)

        Args:
            sql: SQL statement to execute
            params: Optional query parameters for parameterized queries
        """
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = params

        query_job = self.client.query(sql, job_config=job_config)
        query_job.result()  # Wait for completion

    def export_table_to_gcs(
        self,
        table_id: str,
        destination_uri: str,
        format: str = "NEWLINE_DELIMITED_JSON"
    ) -> None:
        """Export table to Google Cloud Storage"""
        full_table_id = f"{settings.PROJECT_ID}.{self.dataset_id}.{table_id}"
        table = self.client.get_table(full_table_id)

        job_config = bigquery.ExtractJobConfig()
        job_config.destination_format = format

        extract_job = self.client.extract_table(
            table,
            destination_uri,
            job_config=job_config,
        )
        extract_job.result()  # Wait for completion

# Global instance
bigquery_service = BigQueryService()
