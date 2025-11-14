import boto3
import os
from datetime import datetime

def upload_template_to_s3():
    """Upload PPT template to S3 with proper settings"""
    
    # S3 configuration
    bucket_name = "capstone-presentations-dev-mujdzvu6"
    region = "ap-southeast-1"
    template_file = "PPT_Template.pptx"
    s3_key = "templates/PPT_Template.pptx"
    
    # Check if file exists
    if not os.path.exists(template_file):
        print(f"Template file not found: {template_file}")
        return False
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        # Upload with metadata and proper content type
        with open(template_file, 'rb') as file_data:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                Metadata={
                    'purpose': 'template',
                    'project': 'capstone',
                    'uploaded-by': 'kaijun',
                    'upload-date': datetime.now().isoformat(),
                    'original-filename': template_file
                },
                ServerSideEncryption='AES256'  # Ensure encryption
            )
        
        print(f"Location: s3://{bucket_name}/{s3_key}")
        
        # Verify upload by getting object metadata
        response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        file_size = response['ContentLength']
        last_modified = response['LastModified']
        
        print(f"File size: {file_size:,} bytes")
        print(f"Last modified: {last_modified}")
        print(f"Encryption: {response.get('ServerSideEncryption', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False

def get_template_urls():
    """Get various URLs for the uploaded template"""
    bucket_name = "capstone-presentations-dev-mujdzvu6"
    region = "ap-southeast-1"
    s3_key = "templates/PPT_Template.pptx"
    
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        # 1. Direct S3 URL (won't work due to private bucket)
        direct_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        
        # 2. Generate presigned URL (temporary access)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        # 3. Generate presigned URL for longer access (24 hours)
        long_presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=86400  # 24 hours
        )
        
        print(f"Template URLs:")
        print(f"S3 URI: s3://{bucket_name}/{s3_key}")
        print(f"Direct URL (private): {direct_url}")
        print(f"Presigned URL (1h): {presigned_url}")
        print(f"Presigned URL (24h): {long_presigned_url}")
        
        return {
            's3_uri': f"s3://{bucket_name}/{s3_key}",
            'direct_url': direct_url,
            'presigned_1h': presigned_url,
            'presigned_24h': long_presigned_url
        }
        
    except Exception as e:
        print(f"Error generating URLs: {str(e)}")
        return None

# Add this to the main section
if __name__ == "__main__":
    print("Uploading PPT template to S3...")
    success = upload_template_to_s3()
    
    if success:
        print("\n" + "="*50)
        get_template_urls()  # Add this line