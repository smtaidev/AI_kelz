#!/usr/bin/env python3
"""
Quality Review Router
FastAPI router for quality review endpoints
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path


from app.services.deviation.quality_review.quality_review import QualityReviewer
from app.services.deviation.quality_review.quality_review_schema import VoiceQualityReviewResponse

# Create router
router = APIRouter()


quality_reviewer = QualityReviewer()


@router.post(
    "/quality-review/",
    tags=["deviation"],
    summary="Quality Review",
    description="Upload a document, a voice file, or both, and get a quality/SME review with extracted and transcribed text."
)
async def quality_review(
    file: UploadFile = File(None),
    voice_file: UploadFile = File(None),
    transcribed_text: str = Form(""),
    action_summary: str = Form("")
):
    """
    Quality Review endpoint with 4 user input options:
    - file: Optional document file (pdf, docx, doc, txt, rtf)
    - voice_file: Optional audio file (mp3, wav, m4a, mp4, webm, ogg, flac)
    - transcribed_text: Optional direct text input
    - action_summary: Optional summary or checklist for review
    Returns review summary, transcribed text, and extracted document text.
    """
    import uuid
    from app.services.utils.transcription import transcribe_audio
    from app.services.utils.document_ocr import DocumentOCR
    temp_dir = tempfile.gettempdir()
    response_data = {}
    temp_paths = []
    try:
        # Handle voice file upload and transcription
        if voice_file:
            file_extension = os.path.splitext(voice_file.filename)[1]
            temp_path = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex}{file_extension}")
            content = await voice_file.read()
            with open(temp_path, 'wb') as f:
                f.write(content)
            transcribed_text_result = transcribe_audio(temp_path)
            if not transcribed_text_result:
                raise Exception("Transcription failed or returned empty text.")
            response_data["transcribed_text"] = transcribed_text_result
            temp_paths.append(temp_path)
        else:
            transcribed_text_result = transcribed_text
        # Handle document file upload and extraction
        processed_document_text = None
        if file:
            doc_extension = os.path.splitext(file.filename)[1]
            doc_temp_path = os.path.join(temp_dir, f"review_{uuid.uuid4().hex}{doc_extension}")
            doc_content = await file.read()
            with open(doc_temp_path, 'wb') as doc_f:
                doc_f.write(doc_content)
            document_ocr = DocumentOCR()
            processed_document_text = document_ocr.process_file(doc_temp_path)
            response_data["extracted_document_text"] = processed_document_text
            temp_paths.append(doc_temp_path)
        # Run the quality review logic
        # Here, you would call your main review logic, passing transcribed_text_result, processed_document_text, and action_summary
        # For demonstration, we'll call process_voice_for_quality_review if transcribed_text_result exists, else just return extracted doc text
        if transcribed_text_result:
            result = quality_reviewer.process_voice_for_quality_review(temp_paths[0] if temp_paths else None)
            response_data["quality_review"] = result.get("quality_review")
            response_data["sme_review"] = result.get("sme_review")
            response_data["message"] = result.get("message", "Quality review completed successfully")
        elif processed_document_text:
            # If only document, you may want to run a document-based review here
            response_data["message"] = "Document extracted, no voice or text provided."
        else:
            response_data["message"] = "No input provided."
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality review error: {str(e)}")
    finally:
        for p in temp_paths:
            if p and os.path.exists(p):
                os.unlink(p)



