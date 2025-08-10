from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from .qta_review import Review, process_review_with_file
from .qta_review_schema import review_resonse, review_request
import tempfile
import os
import shutil
import uuid
from app.services.utils.transcription import transcribe_audio

router = APIRouter()
review = Review()

@router.post("/review")
async def get_review(
    file: UploadFile = File(None),
    voice_file: UploadFile = File(None),
    transcribed_text: str = Form(""),
    action_summary: str = Form(...)
):
    try:
        response_data = {}
        # If a voice file is uploaded, transcribe it
        if voice_file:
            temp_dir = tempfile.gettempdir()
            file_extension = os.path.splitext(voice_file.filename)[1]
            temp_path = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex}{file_extension}")
            try:
                content = await voice_file.read()
                with open(temp_path, 'wb') as f:
                    f.write(content)
                # Transcribe the audio file
                transcribed_text_result = transcribe_audio(temp_path)
                if not transcribed_text_result:
                    raise Exception("Transcription failed or returned empty text.")
                response_data["transcribed_text"] = transcribed_text_result
                # If a document file is also uploaded, process it
                processed_document_text = None
                if file:
                    doc_extension = os.path.splitext(file.filename)[1]
                    doc_temp_path = os.path.join(temp_dir, f"review_{uuid.uuid4().hex}{doc_extension}")
                    try:
                        doc_content = await file.read()
                        with open(doc_temp_path, 'wb') as doc_f:
                            doc_f.write(doc_content)
                        processed_document_text = review.process_document(doc_temp_path)
                        response_data["extracted_document_text"] = processed_document_text
                    finally:
                        try:
                            if os.path.exists(doc_temp_path):
                                os.remove(doc_temp_path)
                        except Exception:
                            pass
                request = review_request(
                    transcribed_text=transcribed_text_result,
                    processed_document_text=processed_document_text,
                    action_summary=action_summary
                )
                summary = review.get_summary(request)
                response_data["review_summary"] = summary.summary if hasattr(summary, "summary") else summary
                return response_data
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
        # If only a document file is uploaded
        elif file:
            temp_dir = tempfile.gettempdir()
            file_extension = os.path.splitext(file.filename)[1]
            temp_path = os.path.join(temp_dir, f"review_{uuid.uuid4().hex}{file_extension}")
            try:
                content = await file.read()
                with open(temp_path, 'wb') as f:
                    f.write(content)
                processed_document_text = review.process_document(temp_path)
                response_data["extracted_document_text"] = processed_document_text
                response = process_review_with_file(
                    temp_path,
                    transcribed_text,
                    action_summary
                )
                response_data["review_summary"] = response.summary if hasattr(response, "summary") else response
                response_data["transcribed_text"] = transcribed_text
                return response_data
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
        # No file uploads, just text
        else:
            request = review_request(
                transcribed_text=transcribed_text,
                processed_document_text=None,
                action_summary=action_summary
            )
            summary = review.get_summary(request)
            return {
                "review_summary": summary.summary if hasattr(summary, "summary") else summary,
                "transcribed_text": transcribed_text
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
