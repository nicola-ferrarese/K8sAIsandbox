# Test 1: Install and import required packages
import boto3
import botocore.config
import random
from botocore.exceptions import ClientError, EndpointConnectionError

from minio import Minio
import socket
import requests

# Test 1: Basic DNS resolution
print("=== DNS Resolution Test ===")
try:
    ip = socket.gethostbyname('minio.minio.svc.cluster.local')
    print(f"✅ MinIO resolves to: {ip}")
except Exception as e:
    print(f"❌ DNS resolution failed: {e}")

# Test 2: Check if we can resolve shorter names
try:
    ip2 = socket.gethostbyname('minio.minio')
    print(f"✅ minio.minio resolves to: {ip2}")
except Exception as e:
    print(f"❌ minio.minio resolution failed: {e}")

try:
    ip3 = socket.gethostbyname('minio')
    print(f"✅ minio resolves to: {ip3}")
except Exception as e:
    print(f"❌ minio resolution failed: {e}")


try:
    client = Minio(
        'minio.minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )
    buckets = client.list_buckets()
    print("MinIO connection successful!")
    for bucket in buckets:
        print(f"Bucket: {bucket.name}")
except Exception as e:
    print(f"MinIO client connection failed: {e}")

print("Testing MinIO API with requests...")

try:
    # Test the health endpoint first
    health_response = requests.get('http://minio.minio:9000/minio/health/live', timeout=10)
    print(f"✅ Health check: {health_response.status_code}")
    
    # Test a basic S3 API call (this should return 403 without proper auth, but that's expected)
    api_response = requests.get('http://minio.minio:9000/', timeout=10)
    print(f"✅ API endpoint accessible: {api_response.status_code}")
    print(f"Response headers: {dict(api_response.headers)}")
    
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")


# Create a custom config with shorter timeouts and retries
config = botocore.config.Config(
    connect_timeout=10,           # 10 seconds to establish connection
    read_timeout=10,              # 10 seconds to read response
    retries={'max_attempts': 3},  # Retry up to 3 times
    max_pool_connections=10       # Connection pool size
)

print("Starting connection with custom config...")

try:
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio.minio:9000',  # Use the working DNS name
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        config=config,
        region_name='us-east-1'  # Some clients require a region
    )
    
    print("Client created, testing connection...")
    
    # Test with a quick operation
    response = s3_client.list_buckets()
    print("✅ Connected to MinIO successfully!")
    print(f"Buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
    
except ClientError as e:
    print(f"❌ AWS Client Error: {e}")
except EndpointConnectionError as e:
    print(f"❌ Endpoint Connection Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"Error type: {type(e)}")


# Create a MinIO Bucket and populate it with a test file
try:
    bucket_name = 'test-bucket'
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio.minio:9000',  # Use the working DNS name
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        config=config,
        region_name='us-east-1'  # Some clients require a region
    )

    # Create the bucket if it doesn't exist
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"ℹ️ Bucket '{bucket_name}' already exists and is owned by you.")
        else:
            print(f"❌ Error creating bucket: {e}")
            raise
    
    # Upload a test file
    test_data = b'This is a test file.'
    s3_client.put_object(Bucket=bucket_name, Key=f'test_file_{random.randint(1000, 9999)}.txt', Body=test_data)
    print("✅ Test file uploaded successfully.")
except ClientError as e:
    print(f"❌ AWS Client Error during bucket operations: {e}")
except EndpointConnectionError as e:
    print(f"❌ Endpoint Connection Error during bucket operations: {e}")
except Exception as e:
    print(f"❌ Unexpected error during bucket operations: {e}")
    print(f"Error type: {type(e)}")