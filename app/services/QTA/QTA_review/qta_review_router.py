import os
import tempfile
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.QTA.QTA_review.qta_review_schema import (
    per_minute_qta_review_request, 
    per_minute_qta_review_response, 
    final_qta_review_request, 
    final_qta_review_response,
    repeat_qta_review_request
)
from app.services.QTA.QTA_review.qta_review import QTAreview
from app.services.utils.convert_file import FileConverter
from app.services.utils.document_ocr import DocumentOCR
from typing import Optional, Dict, Any

router = APIRouter(prefix="/qta-review", tags=["qta-review"])
converter=FileConverter()
qta_service = QTAreview()
document_ocr = DocumentOCR()

@router.post("/per-minute-qta-review", response_model=per_minute_qta_review_response)
async def process_per_minute_review(request: per_minute_qta_review_request):
    """
    Process per-minute QTA review with direct text input
    """
    try:
        result = qta_service.get_per_minute_summary(request)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing per-minute review: {str(e)}"
        )

@router.post("/final-qta-review", response_model=final_qta_review_response)
async def process_final_review(
   request:final_qta_review_request
):
    """
    Process final QTA review using transcribed text, the original document (as string),
    and an optional uploaded reference document file.
    """
    try:
        result = qta_service.get_final_summary(request)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing final review: {str(e)}"
        )





@router.post("/final-qta-review-repeat", response_model=final_qta_review_response)
async def process_final_review_repeat(request: repeat_qta_review_request):
    try:
        result = qta_service.repeat_final_summary(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing repeat final review: {str(e)}"
        )

