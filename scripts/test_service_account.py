#!/usr/bin/env python3
"""Test service account permissions"""

import os
from google.cloud import bigquery, storage
from dotenv import load_dotenv

load_dotenv()

def test_bigquery():
    """Test BigQuery access"""
    try:
        client = bigquery.Client()
        print(f"✅ BigQuery: Connected as project '{client.project}'")

        # List datasets
        datasets = list(client.list_datasets())
        print(f"✅ BigQuery: Can list datasets ({len(datasets)} found)")

        if datasets:
            for dataset in datasets[:3]:  # Show first 3
                print(f"   - {dataset.dataset_id}")

        # Try query
        query = "SELECT 1 as test, CURRENT_TIMESTAMP() as now"
        results = list(client.query(query).result())
        print(f"✅ BigQuery: Can run queries")

        return True
    except Exception as e:
        print(f"❌ BigQuery Error: {e}")
        return False

def test_storage():
    """Test Cloud Storage access"""
    try:
        client = storage.Client()
        bucket_name = os.getenv('GCS_BUCKET')

        if not bucket_name:
            print("⚠️  Storage: GCS_BUCKET not set in .env")
            print("   Set GCS_BUCKET in .env to test storage access")
            return None

        bucket = client.bucket(bucket_name)

        # Check if bucket exists
        if bucket.exists():
            print(f"✅ Storage: Can access bucket '{bucket_name}'")

            # List objects
            blobs = list(bucket.list_blobs(max_results=5))
            print(f"✅ Storage: Can list objects ({len(blobs)} found)")

            if blobs:
                for blob in blobs[:3]:  # Show first 3
                    print(f"   - {blob.name}")

            return True
        else:
            print(f"❌ Storage: Bucket '{bucket_name}' does not exist")
            print(f"   Create it with: gsutil mb -p PROJECT_ID -l asia-southeast1 gs://{bucket_name}")
            return False

    except Exception as e:
        print(f"❌ Storage Error: {e}")
        return False

def test_dataset():
    """Test if retail_branches dataset exists"""
    try:
        client = bigquery.Client()
        project_id = os.getenv('PROJECT_ID')
        dataset_id = os.getenv('DATASET_ID', 'retail_branches')

        if not project_id:
            print("⚠️  Dataset: PROJECT_ID not set in .env")
            return None

        full_dataset_id = f"{project_id}.{dataset_id}"

        try:
            dataset = client.get_dataset(full_dataset_id)
            print(f"✅ Dataset: '{dataset_id}' exists")

            # List tables
            tables = list(client.list_tables(dataset))
            print(f"✅ Dataset: Contains {len(tables)} table(s)")

            if tables:
                for table in tables[:5]:  # Show first 5
                    print(f"   - {table.table_id}")
            else:
                print("   ⚠️  No tables found. Run: python scripts/setup_bigquery.py")

            return True
        except Exception:
            print(f"❌ Dataset: '{dataset_id}' does not exist")
            print(f"   Create it with: python scripts/setup_bigquery.py")
            return False

    except Exception as e:
        print(f"❌ Dataset Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Service Account Permissions")
    print("=" * 60)

    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('PROJECT_ID')

    if creds_path:
        print(f"📄 Credentials: {creds_path}")
        if not os.path.exists(creds_path):
            print(f"   ⚠️  WARNING: File does not exist!")
    else:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        print("   Using default credentials (gcloud auth application-default login)")

    if project_id:
        print(f"🌍 Project ID: {project_id}")
    else:
        print("⚠️  PROJECT_ID not set in .env")

    print()

    # Run tests
    bigquery_ok = test_bigquery()
    print()

    dataset_ok = test_dataset()
    print()

    storage_ok = test_storage()

    print()
    print("=" * 60)

    # Summary
    if bigquery_ok and (dataset_ok or dataset_ok is None):
        print("✅ BigQuery: All tests passed!")
    else:
        print("❌ BigQuery: Some tests failed")

    if storage_ok:
        print("✅ Storage: All tests passed!")
    elif storage_ok is None:
        print("⚠️  Storage: Not configured (optional)")
    else:
        print("❌ Storage: Tests failed")

    print("=" * 60)

    if bigquery_ok and dataset_ok:
        print("\n✅ Ready to use! You can now:")
        print("1. Create test user: python scripts/create_test_user.py")
        print("2. Start the app: ./scripts/run_local.sh")
    elif bigquery_ok and not dataset_ok:
        print("\n⚠️  Next step:")
        print("Run: python scripts/setup_bigquery.py")
    else:
        print("\n❌ Please fix the errors above before continuing")
