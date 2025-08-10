#!/usr/bin/env python3
"""
Enhanced AI Analysis Module
Improved incident analysis with better prompting and parsing
"""

import requests
import json
import re
import os
import sys

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

from app.config.config import OPENAI_API_KEY

class AIAnalyzer:
    def __init__(self):
        # Load configuration from environment
        self.openai_api_key = OPENAI_API_KEY
        
        # Validate API key
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def analyze_with_prompt(self, prompt: str) -> str:
        """
        Analyze content with a custom prompt and return the AI's response as a string.
        Enhanced with better error handling and debugging.
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert pharmaceutical deviation investigator with extensive experience in GMP compliance, quality systems, and regulatory requirements. Provide detailed, actionable analysis based on industry best practices.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 4000,
                'temperature': 0.3,
                'top_p': 0.9
            }
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=120
            )
            print("DEBUG: Raw AI response:", response.text)
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                if not ai_response:
                    return None
                if len(ai_response) < 100:
                    return ai_response
                return ai_response
            elif response.status_code == 429:
                return None
            elif response.status_code == 401:
                return None
            elif response.status_code == 400:
                return None
            else:
                return None
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.RequestException:
            return None
        except json.JSONDecodeError:
            return None
        except Exception:
            import traceback
            return None

    def analyze_incident(self, transcribed_text):
        """
        Analyze transcribed text and extract incident information
        """
        try:
            structured_data = self._get_structured_analysis(transcribed_text)
            if structured_data:
                return structured_data
            else:
                return None
        except Exception as e:
            return None

    def _get_structured_analysis(self, transcribed_text):
        """
        Get structured analysis using improved prompting
        """
        try:
            # Truncate the input transcript to avoid context overflow
            max_len = 4000
            truncated_text = transcribed_text[:max_len]
            prompt = f"""
INSTRUCTIONS:
- Treat any event, referral, case, or situation in the transcript as an "incident" for the purpose of this analysis, even if it is not a pharmaceutical deviation or GMP event.
- Fill out EVERY field below using all information from the transcript (audio, document, or both).
- For the fields deviation_triage, product_quality, patient_safety, regulatory_impact, validation_impact, customer_notification, review_qta, and criticality, ALWAYS make a best-guess assessment based on your analysis, even if the transcript does not mention them. Do NOT leave these fields blank or as "Not specified"—always provide your best judgment.
- If a field is not explicit, infer from context or write "Not specified" (except for the above fields, which must always be filled).
- Use the JSON format for PRODUCT_QUALITY, PATIENT_SAFETY, and REGULATORY_IMPACT.
- Do NOT leave any field blank.
- Respond ONLY in the format below, no extra explanation.

===ANALYSIS START===
INCIDENT_TITLE: [Descriptive title]
WHO: [People involved, roles, departments]
WHAT: [What happened, sequence of events]
WHERE: [Location, department, facility]
IMMEDIATE_ACTION: [Immediate actions taken]
QUALITY_CONCERNS: [Quality issues, product/service impact]
QUALITY_CONTROLS: [Controls that failed or were bypassed]
RCA_TOOL: [Root cause analysis method]
EXPECTED_INTERIM_ACTION: [Actions to prevent recurrence]
CAPA: [Corrective and Preventive Actions]

DEVIATION_TRIAGE: [Yes or No]
PRODUCT_QUALITY: [If Yes, JSON: {{"yes_no": "Yes", "level": "High/Medium/Low"}}; if No, {{"yes_no": "No", "level": null}}]
PATIENT_SAFETY: [Same format as PRODUCT_QUALITY]
REGULATORY_IMPACT: [Same format as PRODUCT_QUALITY]
VALIDATION_IMPACT: [Yes or No]
CUSTOMER_NOTIFICATION: [Yes or No]
REVIEW_QTA: [Summary about QTA/customer notification]
CRITICALITY: [Minor or Major]
===ANALYSIS END===

TRANSCRIPT TO ANALYZE:
"""
            prompt += truncated_text
            prompt += """
"""
            print("DEBUG: FINAL AI PROMPT SENT TO OPENAI:\n", prompt)
            analysis_text = self.analyze_with_prompt(prompt)
            print("DEBUG: analysis_text from AI:", analysis_text)
            if analysis_text and self._validate_analysis_text(analysis_text):
                incident_data = self._parse_enhanced_response(analysis_text)
                if incident_data and self._validate_analysis(incident_data):
                    return incident_data
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    def _validate_analysis_text(self, analysis_text):
        """Validate that the analysis text contains meaningful content"""
        if not analysis_text or len(analysis_text) < 50:
            return False
        required_markers = ['INCIDENT_TITLE:', 'WHO:', 'WHAT:', 'WHERE:']
        found_markers = sum(1 for marker in required_markers if marker in analysis_text)
        return found_markers >= 3

    def _parse_enhanced_response(self, analysis_text):
        """
        Parse the enhanced AI response with better error handling
        """
        try:
            incident_data = {
                'title': '',
                'who': '',
                'what': '',
                'where': '',
                'immediate_action': '',
                'quality_concerns': '',
                'quality_controls': '',
                'rca_tool': '',
                'expected_interim_action': '',
                'capa': '',
                'deviation_triage': None,
                'product_quality': None,
                'patient_safety': None,
                'regulatory_impact': None,
                'validation_impact': None,
                'customer_notification': None,
                'review_qta': None,
                'criticality': None
            }
            start_marker = "===ANALYSIS START==="
            end_marker = "===ANALYSIS END==="
            if start_marker in analysis_text and end_marker in analysis_text:
                content = analysis_text.split(start_marker)[1].split(end_marker)[0]
            else:
                content = analysis_text
            patterns = {
                'title': r'INCIDENT_TITLE:\s*(.+?)(?=\n\w+:|$)',
                'who': r'WHO:\s*(.+?)(?=\n\w+:|$)',
                'what': r'WHAT:\s*(.+?)(?=\n\w+:|$)',
                'where': r'WHERE:\s*(.+?)(?=\n\w+:|$)',
                'immediate_action': r'IMMEDIATE_ACTION:\s*(.+?)(?=\n\w+:|$)',
                'quality_concerns': r'QUALITY_CONCERNS:\s*(.+?)(?=\n\w+:|$)',
                'quality_controls': r'QUALITY_CONTROLS:\s*(.+?)(?=\n\w+:|$)',
                'rca_tool': r'RCA_TOOL:\s*(.+?)(?=\n\w+:|$)',
                'expected_interim_action': r'EXPECTED_INTERIM_ACTION:\s*(.+?)(?=\n\w+:|$)',
                'capa': r'CAPA:\s*(.+?)(?=\n\w+:|$)',
                'deviation_triage': r'DEVIATION_TRIAGE:\s*(.+?)(?=\n\w+:|$)',
                'product_quality': r'PRODUCT_QUALITY:\s*(\{.*?\}|.+?)(?=\n\w+:|$)',
                'patient_safety': r'PATIENT_SAFETY:\s*(\{.*?\}|.+?)(?=\n\w+:|$)',
                'regulatory_impact': r'REGULATORY_IMPACT:\s*(\{.*?\}|.+?)(?=\n\w+:|$)',
                'validation_impact': r'VALIDATION_IMPACT:\s*(.+?)(?=\n\w+:|$)',
                'customer_notification': r'CUSTOMER_NOTIFICATION:\s*(.+?)(?=\n\w+:|$)',
                'review_qta': r'REVIEW_QTA:\s*(.+?)(?=\n\w+:|$)',
                'criticality': r'CRITICALITY:\s*(.+?)(?=\n\w+:|$)'
            }
            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    value = re.sub(r'\n\s*', ' ', value)
                    value = re.sub(r'\s+', ' ', value)
                    if key in ['product_quality', 'patient_safety', 'regulatory_impact']:
                        try:
                            value = json.loads(value)
                        except Exception:
                            value = None
                    incident_data[key] = value
            return incident_data
        except Exception as e:
            return None

    def _validate_analysis(self, incident_data):
        """
        Validate that the analysis contains meaningful information
        """
        if not incident_data:
            return False
        title = incident_data.get('title', '').strip()
        what = incident_data.get('what', '').strip()
        if not title or title == 'N/A' or len(title) < 5:
            return False
        if not what or what == 'N/A' or len(what) < 10:
            return False
        return True

    def get_summary_analysis(self, transcribed_text):
        """
        Get a quick summary analysis of the incident
        """
        try:
            prompt = f"""
Provide a brief 2-3 sentence summary of this incident:

"{transcribed_text}"

Focus on: what happened, who was involved, and the key concern.
"""
            return self.analyze_with_prompt(prompt)
        except Exception as e:
            return None



    def analyze_investigation_context(self, context: str) -> dict:
        """
        Specialized method for investigation context analysis.
        """
        investigation_prompt = f"""
        Analyze the following deviation investigation context and provide comprehensive insights:
        
        {context}
        
        Please provide analysis covering:
        1. Background summary
        2. Timeline and affected systems
        3. Root cause analysis
        4. Impact assessment
        5. Corrective and preventive action recommendations
        6. Risk evaluation and compliance implications
        
        Format the response as a structured JSON analysis suitable for pharmaceutical deviation investigations.
        
        Use this structure:
        {{
            "background_summary": "Investigation analysis based on provided context and deviation data",
            "discussion": {{
                "timeline": "Event timeline constructed from available information",
                "affected_systems": ["Systems identified from context analysis"],
                "initial_findings": "Preliminary findings based on incident description and background"
            }},
            "root_cause_analysis": {{
                "primary_cause": "Root cause identified through systematic analysis",
                "contributing_factors": ["Contributing factors derived from context"],
                "methodology": "Structured root cause analysis methodology applied",
                "evidence": ["Evidence gathered from provided documentation"]
            }},
            "final_assessment": {{
                "impact_analysis": "Comprehensive impact assessment based on triage data",
                "risk_evaluation": "Risk evaluation considering all factors",
                "compliance_implications": "Regulatory and compliance considerations",
                "recurrence_probability": "Likelihood assessment of similar incidents"
            }},
            "capa_recommendations": {{
                "immediate_actions": ["Immediate corrective actions recommended"],
                "long_term_actions": ["Long-term preventive measures suggested"],
                "responsible_parties": ["Recommended responsible parties"],
                "timeline": "Suggested implementation timeline"
            }},
            "ai_generated_insights": {{
                "pattern_analysis": "Analysis of patterns and trends",
                "risk_mitigation": "Additional risk mitigation strategies",
                "process_improvements": ["Process improvement recommendations"],
                "monitoring_recommendations": ["Ongoing monitoring suggestions"]
            }}
        }}
        """
        try:
            response = self.analyze_with_prompt(investigation_prompt)
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "analysis": response,
                    "status": "text_response",
                    "requires_manual_parsing": True
                }
        except Exception as e:
            return {
                "analysis": f"Investigation analysis failed: {str(e)}",
                "status": "error"
            }

    @staticmethod
    def analyze_prompt(prompt):
        """
        Generic method to analyze any prompt using OpenAI
        """
        try:
            analyzer = AIAnalyzer()
            response_text = analyzer.analyze_with_prompt(prompt)
            if response_text:
                return {
                    "analysis": response_text,
                    "status": "success"
                }
            else:
                return {
                    "analysis": "Analysis failed - no response received",
                    "status": "error"
                }
        except Exception as e:
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "status": "error"
            }
