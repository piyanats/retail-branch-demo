#!/usr/bin/env python3
"""Setup BigQuery dataset and tables for Retail Branch Management System"""

from google.cloud import bigquery
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv('DATASET_ID', 'retail_branches')
LOCATION = os.getenv('BIGQUERY_LOCATION', 'asia-southeast1')

if not PROJECT_ID:
    print("❌ ERROR: PROJECT_ID not set in .env file")
    sys.exit(1)

print("=" * 60)
print("BigQuery Setup for Retail Branch Management System")
print("=" * 60)
print(f"Project ID: {PROJECT_ID}")
print(f"Dataset ID: {DATASET_ID}")
print(f"Location: {LOCATION}")
print("=" * 60)

# Initialize BigQuery client
try:
    client = bigquery.Client(project=PROJECT_ID)
    print("✅ Connected to BigQuery")
except Exception as e:
    print(f"❌ Failed to connect to BigQuery: {e}")
    print("\nMake sure:")
    print("1. GOOGLE_APPLICATION_CREDENTIALS is set in .env")
    print("2. Service account has BigQuery permissions")
    sys.exit(1)

# Create dataset
dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = LOCATION

try:
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"✅ Dataset {dataset_id} created or already exists")
except Exception as e:
    print(f"❌ Failed to create dataset: {e}")
    sys.exit(1)

# Define table schemas
tables_sql = {
    'branches': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.branches` (
          branch_id STRING NOT NULL,
          branch_name STRING NOT NULL,
          address STRING,
          province STRING,
          district STRING,
          subdistrict STRING,
          postal_code STRING,
          phone STRING,
          status STRING,
          dc_code STRING,
          estimate_opening_date DATE,
          actual_opening_date DATE,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          created_by STRING,
          updated_by STRING
        )
    """,

    'documents': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.documents` (
          document_id STRING NOT NULL,
          branch_id STRING NOT NULL,
          document_type STRING NOT NULL,
          document_name STRING NOT NULL,
          file_path STRING NOT NULL,
          file_size INT64,
          mime_type STRING,
          team STRING NOT NULL,
          uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          uploaded_by STRING
        )
    """,

    'users': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.users` (
          user_id STRING NOT NULL,
          email STRING NOT NULL,
          name STRING NOT NULL,
          user_level STRING NOT NULL,
          is_active BOOLEAN DEFAULT TRUE,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          last_login TIMESTAMP
        )
    """,

    'user_teams': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.user_teams` (
          user_team_id STRING NOT NULL,
          user_id STRING NOT NULL,
          team_name STRING NOT NULL,
          role STRING NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          created_by STRING
        )
    """,

    'legal_ppp09': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.legal_ppp09` (
          ppp09_id STRING NOT NULL,
          branch_id STRING NOT NULL,
          ppp09_number STRING,
          issue_date DATE,
          expiry_date DATE,
          owner_name STRING,
          address_number STRING,
          address_moo STRING,
          address_trok STRING,
          address_soi STRING,
          address_road STRING,
          address_tambon STRING,
          address_amphoe STRING,
          address_province STRING,
          address_postal_code STRING,
          land_area_rai FLOAT64,
          land_area_ngan FLOAT64,
          land_area_wa FLOAT64,
          building_area_sqm FLOAT64,
          annual_tax_amount FLOAT64,
          payment_status STRING,
          pdf_file_path STRING,
          pdf_file_size INT64,
          pdf_uploaded_at TIMESTAMP,
          pdf_uploaded_by STRING,
          remarks STRING,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          created_by STRING,
          updated_by STRING
        )
    """,

    'audit_logs': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.audit_logs` (
          log_id STRING NOT NULL,
          user_id STRING NOT NULL,
          user_email STRING NOT NULL,
          action_type STRING NOT NULL,
          resource_type STRING,
          resource_id STRING,
          action_detail STRING,
          ip_address STRING,
          user_agent STRING,
          status STRING,
          error_message STRING,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
        PARTITION BY DATE(created_at)
        OPTIONS(
          partition_expiration_days=2555
        )
    """,

    'dc_changes': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.dc_changes` (
          dc_change_id STRING NOT NULL,
          branch_id STRING NOT NULL,
          current_dc STRING NOT NULL,
          new_dc STRING NOT NULL,
          effective_date DATE NOT NULL,
          reason STRING,
          status STRING DEFAULT 'scheduled',
          completed_at TIMESTAMP,
          error_message STRING,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
          created_by STRING
        )
    """,

    'provinces': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.provinces` (
          province_id STRING NOT NULL,
          province_name_th STRING NOT NULL,
          province_name_en STRING,
          region STRING
        )
    """,

    'districts': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.districts` (
          district_id STRING NOT NULL,
          district_name_th STRING NOT NULL,
          district_name_en STRING,
          province_id STRING NOT NULL
        )
    """,

    'subdistricts': """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.subdistricts` (
          subdistrict_id STRING NOT NULL,
          subdistrict_name_th STRING NOT NULL,
          subdistrict_name_en STRING,
          district_id STRING NOT NULL,
          postal_code STRING
        )
    """
}

# Create tables
print("\nCreating tables...")
print("-" * 60)

for table_name, sql in tables_sql.items():
    try:
        formatted_sql = sql.format(project=PROJECT_ID, dataset=DATASET_ID)
        query_job = client.query(formatted_sql)
        query_job.result()  # Wait for completion
        print(f"✅ Table '{table_name}' created or already exists")
    except Exception as e:
        print(f"❌ Failed to create table '{table_name}': {e}")

print("-" * 60)
print("\n✅ BigQuery setup completed!")
print("\nNext steps:")
print("1. Run: python scripts/create_test_user.py")
print("2. Start the app: ./scripts/run_local.sh")
print("3. Visit: http://localhost:8000/login")
print("=" * 60)
