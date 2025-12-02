import os
import json
import openai
from fastapi import HTTPException
from dotenv import load_dotenv
from .qta_review_schema import per_minute_qta_review_request, per_minute_qta_review_response, final_qta_review_request, final_qta_review_response, repeat_qta_review_request
from app.services.utils.document_ocr import DocumentOCR

load_dotenv()

class QTAreview:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.document_ocr = DocumentOCR()
    


    def get_per_minute_summary(self, input_data: per_minute_qta_review_request) -> per_minute_qta_review_response:
        import json

        transcribed_text = json.dumps(input_data.transcribed_text)
        existing_quality_review = json.dumps(input_data.quality_review or [])

        prompt = f"""
                You are an Expert QTA Reviewer that receives audio transcript {transcribed_text} related to quality and change processes. Your task is to analyze the text and determine whether any of the following quality review aspects are discussed.

                You may also receive existing details from earlier reviews {existing_quality_review}. If an item was already covered previously, you must still include it in your response if it is present in the new text.

                **Change Summary**: Provide detailed summary of actions to be completed by AI on attachment or new documents as required auto transcription.

                **Review Summary**: Observations and findings (e.g., "Temperature excursion in storage area. Product stored above acceptable limits").

                Quality Review Criteria to Analyze:
                • Have list of actions in action summary been completed satisfactorily?  
                • Are content updates satisfactory?  
                • Are template updates satisfactory?  
                • Is the evidence compliant with data integrity?  
                • SME Inputs and Concerns

                Instructions:
                1. Analyze the transcript and update the quality_review, change_summary, and review_summary based on the content.
                2. Include both new and previously covered relevant details, preserving existing information.
                3. Respond ONLY with valid JSON, no markdown, no explanations.
                4. Your output must follow the structure below:

                {{
                "quality_review": [
                  {{"Actions Completed": "Description of completion status"}},
                  {{"Content Updates": "Assessment of content updates"}},
                  {{"Template Updates": "Assessment of template updates"}}
                ],
                "change_summary": "Single string with detailed summary of actions to be completed by AI on attachment or new documents",        
                "review_summary": "Single string with observations and findings from the review"
                }}
                """

        response = self.get_openai_response(prompt).strip()

        try:
            response_dict = json.loads(response)
        except json.JSONDecodeError as e:
            print("Model response:", response)
            raise HTTPException(status_code=500, detail="Failed to parse model response as JSON.")

        return per_minute_qta_review_response(**response_dict)

    
    def get_final_summary(self, input_data:final_qta_review_request) -> final_qta_review_response:
        """Process review request with optional document text"""
        prompt = self.create_prompt(input_data)
        
        
        response = self.get_openai_response(prompt)
        print(response)
        response_dict = json.loads(response)
        return final_qta_review_response(**response_dict)

    def create_prompt(self, input_data: final_qta_review_request) -> str:
        return f"""
                You are an AI assistant responsible for updating a client document.

                Your task is to revise the **original_document** using:
                1. The user's instructions provided in the **transcribed_text**.
                2. The **reference_document** (if provided), which is a dictionary containing multiple filename(s) as keys and their respective document content as values - use these as references for how the document should be structured or what content to include.

                ### Instructions:
                - First, analyze the **transcribed_text** to extract key instructions or intent behind the changes.
                - If **reference_document** is provided, examine the document(s) within it to understand the desired structure, content, or formatting.
                - Apply the user instructions to update the **original_document**, using the reference document(s) as guidance when available.
                - If no reference document is provided, rely solely on the transcribed instructions.

                Your response must be a valid JSON object with the following fields:

                - **quality_review**: A list of objects where criterion names are keys and assessments are values (e.g., [{{\"Actions Completed\": \"All actions satisfactorily completed\"}}, {{\"Content Updates\": \"Content updates are satisfactory\"}}, {{\"Data Integrity\": \"Evidence compliant with data integrity standards\"}}]).
                - **change_summary**: A single string with detailed summary of actions to be completed by AI on attachment or new documents as required auto transcription.
                - **review_summary**: A single string with observations and findings from the review (e.g., "Temperature excursion in storage area. Product stored above acceptable limits").
                - **document_text**: The full revised version of the original document, reflecting all relevant changes.

                **CRITICAL**: 
                - quality_review must be a list of objects (not strings)
                - change_summary must be a single string (not an array)
                - review_summary must be a single string (not an array)

                ### User Instructions:
                {input_data.transcribed_text}

                ### Reference Document(s):
                {input_data.reference_document if input_data.reference_document else 'No reference document provided'}

                ### Original Document (To Be Updated):
                {input_data.original_document}

                Generate the updated document and return the full response as a structured JSON object.

                Example format:
                {{
                  "quality_review": [
                    {{"Actions Completed": "Description of completion status"}},
                    {{"Content Updates": "Assessment of content updates"}},
                    {{"Template Updates": "Assessment of template updates"}}
                  ],
                  "change_summary": "Single string describing actions completed on documents",
                  "review_summary": "Single string with observations and findings",
                  "document_text": "Full updated document text here..."
                }}
                """

                
    def repeat_final_summary(self, input_data: repeat_qta_review_request) -> final_qta_review_response:
        prompt = f"""
        You are an AI assistant tasked with revising a client document based on user-provided feedback.

        ### Instructions:
        1. Carefully review the user changes below and interpret the intended modifications:
        {input_data.transcribed_text}

        2. Apply these changes to the existing document:
        {input_data.document}

        3. Based on the applied updates, revise the following summaries as needed:
        - Existing Quality Review: {input_data.quality_review}
        - Existing Change Summary: {input_data.change_summary}
        - Existing Review Summary: {input_data.review_summary}

        ### Response Format:
        Return a valid JSON object with the following fields:
        - "quality_review": List of objects where criterion names are keys and assessments are values
        - "change_summary": Single string with detailed summary of actions to be completed by AI on attachment or new documents as required auto transcription
        - "review_summary": Single string with observations and findings from the review (e.g., "Temperature excursion in storage area. Product stored above acceptable limits")
        - "document_text": The fully revised client document incorporating the user changes

        Example format:
        {{
          "quality_review": [
            {{"Actions Completed": "Description of completion status"}},
            {{"Content Updates": "Assessment of content updates"}},
            {{"Template Updates": "Assessment of template updates"}}
          ],
          "change_summary": "Single string describing actions completed on documents",
          "review_summary": "Single string with observations and findings",
          "document_text": "Full updated document text here..."
        }}

        ### Important:
        - Return **only** the JSON object. No explanations or extra text.
        - Make sure the JSON is well-formatted and valid.

        Begin processing now and return only the final JSON output.
        """
        
        try:
            response_text = self.get_openai_response(prompt)
            parsed = json.loads(response_text)
            return final_qta_review_response(**parsed)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nRaw response:\n{response_text}")
        except Exception as e:
            raise ValueError(f"Error in repeat final summary: {e}")

    
    def get_openai_response (self, prompt:str)->str:
        completion =self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7            
        )
        return completion.choices[0].message.content




