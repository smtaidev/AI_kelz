import os
import json
import openai
from fastapi import HTTPException
from dotenv import load_dotenv
from .QTA_revision_schema import per_minute_qta_revision_request, per_minute_qta_revision_response, final_qta_revision_request, final_qta_revision_response, repeat_qta_revision_request
from app.services.utils.document_ocr import DocumentOCR
from pydantic import ValidationError


load_dotenv()

class QTARevision:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.document_ocr = DocumentOCR()
    


    def get_per_minute_summary(self, input_data: per_minute_qta_revision_request) -> per_minute_qta_revision_response:
        try:
            system_prompt = """You are a language model specialized in analyzing audio transcriptions related to quality and change processes.

Your task: Analyze transcriptions and extract key information about quality processes, updating existing information appropriately.

Key topics to detect:
- Change Details (Upload change requests, Change control processes)
- CAPA (Corrective and Preventive Actions)
- SME (Subject Matter Expert) Inputs and Concerns
- Gap Assessment (especially about in-house vs external templates)

Response format: Return ONLY valid JSON with exactly two keys:
- "changed_details": A SINGLE STRING containing markdown-formatted bullet points (use \\n to separate lines)
- "action_summary": A SINGLE STRING containing bullet points for actions (use \\n to separate lines)

CRITICAL: Both fields must be STRINGS, not arrays or lists!

Example format:
{
  "changed_details": "- **Topic 1**: Description here\\n- **Topic 2**: Another description",
  "action_summary": "- Action item 1\\n- Action item 2\\n- Action item 3"
}

JSON formatting rules:
- Use \\n for line breaks within strings, never actual line breaks
- Both values must be single strings with \\n separators, NOT arrays
- Preserve existing relevant content when provided
- Ensure proper JSON escaping of quotes and special characters
- Return only the JSON object, no explanations or additional text"""

            user_prompt = f"""Analyze this transcription and update the information:

Transcription: {input_data.transcribed_text}

Existing changed details: {input_data.changed_details if input_data.changed_details else "None"}
Existing action summary: {input_data.action_summary if input_data.action_summary else "None"}

Provide updated JSON response with changed_details and action_summary."""

            response = self.get_openai_response(user_prompt, system_prompt)
            print(f"Per-minute response: {response}")
            
            if not response or response.strip() == "":
                raise ValueError("Empty response from OpenAI")
            
            response_dict = json.loads(response)
            return per_minute_qta_revision_response(**response_dict)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {response}")
            raise HTTPException(status_code=500, detail=f"Failed to parse model response as JSON: {str(e)}")
        except ValidationError as e:
            raise HTTPException(status_code=500, detail=f"Response validation failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in get_per_minute_summary: {str(e)}")
    
    
    def get_final_summary(self, input_data:final_qta_revision_request) -> final_qta_revision_response:
        """Process review request with optional document text"""
        try:
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_user_prompt(input_data)
            response = self.get_openai_response(user_prompt, system_prompt)
            print(f"OpenAI Response: {response}")
            
            if not response or response.strip() == "":
                raise ValueError("Empty response from OpenAI")
            
            response_dict = json.loads(response)
            return final_qta_revision_response(**response_dict)
        
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse OpenAI response as JSON: {str(e)}")
        except ValidationError as e:
            raise HTTPException(status_code=500, detail=f"Response validation failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in get_final_summary: {str(e)}")

    def create_system_prompt(self) -> str:
        return """You are an AI assistant specialized in QTA (Quality Technical Agreement) document revision.

Your role and capabilities:
- Expert in quality management documents including SOPs, CAPA, SME reviews, Contracts and compliance requirements
- Skilled in document structure analysis and professional formatting
- Focused on maintaining regulatory compliance and quality standards

Your task process:
1. Analyze user instructions to understand exactly what changes are requested
2. Examine all provided documents to understand their content and relationships
3. Apply requested changes to create revised versions of documents
4. Ensure all revisions maintain professional structure and formatting
5. Focus on quality-related aspects like SOPs, CAPA, SME inputs, and compliance requirements

Response requirements:
- Return ONLY valid JSON with exactly three keys: "action_summary", "change_details", "document_text"
- "action_summary": Brief summary of changes made to which documents
- "change_details": Detailed breakdown using markdown formatting with categories like Document Structure Changes, Content Additions/Modifications, Safety and Compliance Updates, Process Improvements
- "document_text": Complete final revised document content (never abbreviated)
- "change_details" must be a single string with \\n for line breaks, not an object or array
- Maintain document formatting and structure in the final output
- If multiple documents are revised, combine them appropriately in document_text

Critical formatting rules:
- Document filenames are dynamic - analyze content to understand what each document contains  
- Include complete revised document text, never use placeholders like "[...]" or "Content continues..."
- Preserve original document structure, numbering, and professional formatting"""
                
                

    def create_user_prompt(self, input_data: final_qta_revision_request) -> str:
        return f"""Please revise the following documents according to the user instructions.

                    User Instructions:
                    {input_data.transcribed_text}

                    Available Documents:
                    {input_data.documents}

                    Provide your response as a JSON object with the three required keys."""
                
                
    def repeat_final_summary(
    self,
    input_data: repeat_qta_revision_request
) -> final_qta_revision_response:
        prompt = f"""
        You are an AI assistant tasked with revising a client document according to user-provided changes and an updated document.

        Instructions:
        1. Carefully analyze the user changes: {input_data.transcribed_text}
        2. Apply these changes to the existing document: {input_data.document_text} to produce a revised document.
        3. Update the existing action summary: {input_data.action_summary} and existing change details: {input_data.change_details} based on the new revisions.

        Your response must be a single JSON object with the following keys:
        - "action_summary": A concise summary of all changes made (as a string).
        - "change_details": A detailed string of changes using markdown formatting. Use bullet points to organize categories (e.g., CAPA, SME Inputs and Concerns, Gap Assessment). This must be a single string, not an object or array.
        - "document_text": The complete final revised client document text (as a string).

        **IMPORTANT**:
        - Return **ONLY** the JSON object, no explanations, no additional text.
        - Ensure the JSON is valid and properly formatted.
        - The "change_details" field must be a STRING with markdown formatting, not an object or array.

        Example format:
        {{
          "action_summary": "Updated contract terms...",
          "change_details": "- **Category 1**: Description of changes\\n- **Category 2**: More changes\\n- **Category 3**: Additional modifications",
          "document_text": "Complete document text here..."
        }}

        Now, proceed with the analysis and revision, then respond with the JSON output only.
        """

        try:
            response_text = self.get_openai_response(prompt)

            parsed = json.loads(response_text)

            return final_qta_revision_response(
                action_summary=parsed["action_summary"],
                change_details=parsed["change_details"],
                document_text=parsed["document_text"]
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nRaw response:\n{response_text}")
        except KeyError as e:
            raise ValueError(f"Missing expected key in LLM response: {e}")
        except ValidationError as e:
            raise ValueError(f"Response validation failed: {e}")
    
    def get_openai_response(self, prompt: str, system_prompt: str = None) -> str:
        try:
            print(f"Sending request to OpenAI with model: gpt-4")
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7            
            )
            
            response_content = completion.choices[0].message.content
            print(f"Received response length: {len(response_content) if response_content else 0}")
            
            if not response_content:
                raise ValueError("OpenAI returned empty response")
                
            return response_content
            
        except Exception as e:
            print(f"Error in OpenAI API call: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")




