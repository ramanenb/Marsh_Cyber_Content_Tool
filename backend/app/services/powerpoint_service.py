"""
PowerPoint Generation Service
Handles the creation of PowerPoint presentations from incident data
"""
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import uuid
import boto3
import requests
import re
from datetime import datetime, timedelta, timezone
import shutil
from pathlib import Path

# PowerPoint libraries
from pptx import Presentation
from pptx.util import Inches
from copy import deepcopy

# LangChain
from langchain_core.messages import HumanMessage

# Import shared config
from app.config.settings import (
    llm,
    S3_BUCKET_NAME,
    S3_REGION,
    TEMPLATE_S3_KEY,
    LOGO_DEV_TOKEN,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

# Initialize S3 client with credentials from settings
s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# ==================== PYDANTIC MODELS ====================
class ArticlePayload(BaseModel):
    source: str
    executive_summary: str
    background: str
    malicious_activity: str
    outcomes_and_losses: str
    reference_text: str
    summarised_text: str
    source_url: str
    affected_organization: str
    hallucination_classification: Optional[str] = None
    hallucination_explanation: Optional[str] = None
    summarizer_classification: Optional[str] = None
    summarizer_explanation: Optional[str] = None

class PPTGenerationRequest(BaseModel):
    query: str
    industries: Optional[List[str]] = []
    region: Optional[str] = ""
    shortlisted_articles: List[ArticlePayload]

class PPTGenerationResponse(BaseModel):
    success: bool
    presentation_id: str
    download_url: str
    expires_at: str
    articles_processed: int
    message: str

# ==================== UTILITY FUNCTIONS ====================
async def download_template_from_s3() -> str:
    """Download PPT template from S3 to temporary location"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
        temp_path = temp_file.name
        temp_file.close()
        
        s3_client.download_file(S3_BUCKET_NAME, TEMPLATE_S3_KEY, temp_path)
        return temp_path
        
    except Exception as e:
        print(f"Error downloading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download template: {str(e)}")

async def upload_result_to_s3(
    local_file_path: str, 
    presentation_id: str,
    query: str = "",
    industries: List[str] = None,
    region: str = "",
    articles_count: int = 0
) -> str:
    """Upload generated presentation to S3 with metadata"""
    try:
        filename = f"presentation_{presentation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        s3_key = f"generated/{filename}"
        
        # Prepare metadata (S3 metadata keys must be lowercase and no special chars)
        metadata = {
            'presentation-id': presentation_id,
            'query': query[:256] if query else "",  # S3 metadata has 2KB limit per key
            'industries': ','.join(industries) if industries else "",
            'region': region if region else "",
            'articles-count': str(articles_count),
            'created-date': datetime.now().isoformat()
        }
        
        with open(local_file_path, 'rb') as file_data:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_data,
                ContentType='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                ServerSideEncryption='AES256',
                Metadata=metadata
            )
        return s3_key
        
    except Exception as e:
        print(f"Error uploading result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload result: {str(e)}")

def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """Generate presigned URL for S3 object"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


def list_pptx_with_urls(bucket_name=S3_BUCKET_NAME, prefix="generated/", expiration=604800):

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = []

    # If no files found
    if "Contents" not in response:
        return files

    tz_sg = timezone(timedelta(hours=8))

    for obj in response["Contents"]:
        key = obj["Key"]
        if key.endswith(".pptx"):
            # Generate a presigned URL
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=expiration,
            )

            files.append({
                "filename": key.split("/")[-1],
                "uploaded_at": obj["LastModified"].astimezone(tz_sg).isoformat(),
                "url": presigned_url,
            })

    # Sort newest first (optional)
    files.sort(key=lambda x: x["uploaded_at"], reverse=True)

    return files


# ==================== LOGO FUNCTIONS ====================
async def search_company_domain(company_name: str) -> Optional[str]:
    """Search for company domain using LLM"""
    if not company_name or company_name == "UNKNOWN":
        return None
    
    try:
        search_prompt = f"""
        Find the official website domain for the company: {company_name}
        
        Return ONLY the domain name (e.g., "microsoft.com", "apple.com") without http/https or www.
        If you cannot find a specific domain, return "UNKNOWN".
        
        Company: {company_name}
        Domain:
        """
        
        response = llm([HumanMessage(content=search_prompt)])
        domain = response.content.strip().lower()
        
        # Clean up the domain
        domain = re.sub(r'^(https?://)?(www\.)?', '', domain)
        domain = re.sub(r'[^\w\.-]', '', domain)
        
        if domain and domain != "unknown" and "." in domain:
            return domain
        else:
            # print(f"Could not find domain for {company_name}")
            return None
            
    except Exception as e:
        print(f"Error searching domain for {company_name}: {e}")
        return None

async def get_company_logo(company_name: str, temp_dir: str) -> Optional[str]:
    """Fetch company logo using domain search and logo.dev API"""
    if not company_name or company_name == "UNKNOWN":
        return None
    
    # Create safe filename
    safe_filename = re.sub(r'[^a-zA-Z0-9\s]', '', company_name)
    safe_filename = safe_filename.replace(' ', '_').lower()
    filename = os.path.join(temp_dir, f"{safe_filename}_logo.png")
    
    # Search for company domain
    domain = await search_company_domain(company_name)
    if not domain:
        return None
    
    try:
        logo_url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_TOKEN}&retina=true"
        
        response = requests.get(logo_url, timeout=10)
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            print(f"Failed to fetch logo for {company_name} (Status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f" Error fetching logo: {e}")
        return None

# ==================== PPT GENERATION FUNCTIONS ====================
def duplicate_slide(pres: Presentation, index: int):
    """Proper slide duplication using deepcopy"""
    source = pres.slides[index]
    blank_slide_layout = pres.slide_layouts[3]
    new_slide = pres.slides.add_slide(blank_slide_layout)

    for shape in source.shapes:
        el = shape.element
        new_el = deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(new_el, 'p:extLst')

    return new_slide

def replace_text_preserve_formatting(text_frame, placeholder: str, replacement_text: str):
    """Replace placeholder text while preserving formatting"""
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if placeholder in run.text:
                run.text = run.text.replace(placeholder, replacement_text)
                return True
    
    for paragraph in text_frame.paragraphs:
        if placeholder in paragraph.text:
            first_run = paragraph.runs[0] if paragraph.runs else None
            font_name = first_run.font.name if first_run and first_run.font.name else None
            font_size = first_run.font.size if first_run and first_run.font.size else None
            font_bold = first_run.font.bold if first_run else None
            font_italic = first_run.font.italic if first_run else None
            
            font_color = None
            if first_run:
                try:
                    font_color = first_run.font.color.rgb if first_run.font.color else None
                except (AttributeError, TypeError):
                    font_color = None
            
            new_text = paragraph.text.replace(placeholder, replacement_text)
            paragraph.clear()
            new_run = paragraph.add_run()
            new_run.text = new_text
            
            if font_name:
                new_run.font.name = font_name
            if font_size:
                new_run.font.size = font_size
            if font_bold is not None:
                new_run.font.bold = font_bold
            if font_italic is not None:
                new_run.font.italic = font_italic
            if font_color:
                try:
                    new_run.font.color.rgb = font_color
                except (AttributeError, TypeError):
                    pass
            
            return True
    return False

async def populate_slide_with_payload(slide, payload_item: ArticlePayload, temp_dir: str):
    """Populate a single slide with payload data and logo"""
    
    # Get company name and fetch logo
    org_name = payload_item.affected_organization
    company_logo_path = await get_company_logo(org_name, temp_dir)
    
    # Create title
    title = f"Incident: {org_name}"
    if len(title) > 75:
        title = title[:72] + "..."
    
    # Replace placeholders
    placeholders = {
        '{{title}}': title,
        '{{executive_summary}}': payload_item.executive_summary,
        '{{background}}': payload_item.background,
        '{{malicious_activity}}': payload_item.malicious_activity,
        '{{outcomes_and_losses}}': payload_item.outcomes_and_losses
    }
    
    for shape in slide.shapes:
        if hasattr(shape, 'text_frame') and shape.text_frame:
            for placeholder, replacement in placeholders.items():
                if placeholder in shape.text_frame.text:
                    replace_text_preserve_formatting(shape.text_frame, placeholder, replacement)
    
    # Add logo if available
    if company_logo_path and os.path.exists(company_logo_path):
        try:
            left = Inches(0.5)
            top = Inches(0.8)
            height = Inches(0.8)
            width = Inches(1.5)
            slide.shapes.add_picture(company_logo_path, left, top, height=height, width=width)
        except Exception as e:
            print(f"Could not add logo: {e}")
    
    # Add source URL to speaker notes
    source_url = payload_item.source_url or 'No source URL available'
    try:
        slide.notes_slide.notes_text_frame.text = source_url
    except Exception as e:
        print(f"Could not add speaker notes: {e}")

async def build_complete_presentation(payload_list: List[ArticlePayload], template_path: str, output_path: str, temp_dir: str):
    """Build complete presentation with logos and content"""
    # Load template
    prs = Presentation(template_path)
    
    if len(prs.slides) < 2:
        raise ValueError("Template must have at least 2 slides (incident template + ending slide)")
    
    # Duplicate incident template for each payload item except the first
    duplicates_needed = len(payload_list) - 1
    
    for i in range(duplicates_needed):
        org_name = payload_list[i+1].affected_organization
        duplicate_slide(prs, 1)
    
    # Find incident slides (those with template placeholders)
    incident_slides = []
    for i, slide in enumerate(prs.slides):
        has_template_placeholders = False
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame') and shape.text_frame:
                if '{{' in shape.text_frame.text:
                    has_template_placeholders = True
                    break
        
        if has_template_placeholders:
            incident_slides.append((i, slide))
    
    # Populate each incident slide with corresponding payload data
    for idx, (slide_index, slide) in enumerate(incident_slides[:len(payload_list)]):
        if idx < len(payload_list):
            await populate_slide_with_payload(slide, payload_list[idx], temp_dir)
    
    # Save presentation
    prs.save(output_path)
    return output_path

# ==================== SERVICE FUNCTIONS ====================
async def generate_powerpoint_presentation(request: PPTGenerationRequest) -> PPTGenerationResponse:
    """Main service function to generate PowerPoint presentation"""
    
    presentation_id = str(uuid.uuid4())
    temp_dir = None
    template_path = None
    output_path = None
    
    try:
        # Create temporary directory for this request
        temp_dir = tempfile.mkdtemp()
        
        # Download template from S3
        template_path = await download_template_from_s3()
        
        # Create output path
        safe_query = re.sub(r'[^\w\s-]', '', request.query)
        safe_query = re.sub(r'[-\s]+', '_', safe_query)[:50]
        output_filename = f"{safe_query}_{presentation_id}.pptx"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Build presentation
        await build_complete_presentation(
            payload_list=request.shortlisted_articles,
            template_path=template_path,
            output_path=output_path,
            temp_dir=temp_dir
        )
        
        # Upload to S3 with metadata
        s3_key = await upload_result_to_s3(
            local_file_path=output_path,
            presentation_id=presentation_id,
            query=request.query,
            industries=request.industries,
            region=request.region,
            articles_count=len(request.shortlisted_articles)
        )
        
        # Generate presigned download URL (24 hours)
        download_url = generate_presigned_url(s3_key, expiration=86400)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        return PPTGenerationResponse(
            success=True,
            presentation_id=presentation_id,
            download_url=download_url,
            expires_at=expires_at,
            articles_processed=len(request.shortlisted_articles),
            message="Presentation generated successfully!"
        )
        
    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate presentation: {str(e)}"
        )
        
    finally:
        # Cleanup temporary files
        try:
            if template_path and os.path.exists(template_path):
                os.unlink(template_path)
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up: {e}")

async def get_presentation_info(presentation_id: str) -> dict:
    """Get presentation status, download URL, and metadata"""
    try:
        # List objects with the presentation ID
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"generated/presentation_{presentation_id}"
        )
        
        if 'Contents' not in response:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Get the latest file
        latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
        s3_key = latest_file['Key']
        
        # Get object metadata
        head_response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        metadata = head_response.get('Metadata', {})
        
        # Generate new presigned URL
        download_url = generate_presigned_url(s3_key, expiration=3600)
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
        
        return {
            # "presentation_id": presentation_id,
            "download_url": download_url,
            # "expires_at": expires_at,
            # "file_size": latest_file['Size'],
            # "last_modified": latest_file['LastModified'].isoformat(),
            # "metadata": {
            #     "query": metadata.get('query', ''),
            #     "industries": metadata.get('industries', '').split(',') if metadata.get('industries') else [],
            #     "region": metadata.get('region', ''),
            #     "articles_count": int(metadata.get('articles-count', 0)) if metadata.get('articles-count') else 0,
            #     "created_date": metadata.get('created-date', '')
            # }
        }
        
    except Exception as e:
        print(f"Error getting presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get presentation: {str(e)}")
