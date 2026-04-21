"""
Groq Automation Engine - PRODUCTION READY
"""
import json
import os
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# FORCE LOAD .ENV VARIABLES
load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("⚠️ The 'groq' package is not installed. Run: pip install groq")
    GROQ_AVAILABLE = False
    
try:
    from logging_config.logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)

class GroqAutomationEngine:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.groq_available = False
        self.client = None
        self.model = "mixtral-8x7b-32768"
        self.last_api_call = time.time()
        
        if GROQ_AVAILABLE:
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.client = Groq(api_key=api_key)
                self.groq_available = True
                self.logger.info(f"✅ Groq initialized ({self.model})")
            else:
                self.logger.error("❌ [GROQ] API key not found! Please check your .env file.")
    
    def analyze_with_structured_prompt(self, interactive_dom: str, task_prompt: str, current_url: str, iteration: int, workflow_stage: str, recent_failures: list) -> Optional[Dict]:
        if not self.groq_available: return None
        
        failure_warning = ""
        if recent_failures:
            failure_warning = "\n⚠️ DO NOT REPEAT THESE FAILED ACTIONS:\n" + "\n".join([f"- {f}" for f in recent_failures])
            
        sys_prompt = """You are a web automation bot. You will be given an INTERACTIVE DOM list of tagged elements on the screen.
Return ONLY valid JSON.
{
    "analysis": "what is on screen",
    "action_type": "click|fill|scroll|navigate|extract|wait",
    "target": "[data-bot-id='bot-id-X']",
    "value": "text to type or null",
    "reasoning": "why",
    "stage_complete": false,
    "task_complete": false
}
CRITICAL: If clicking/filling, target MUST be formatted exactly like [data-bot-id='bot-id-X'] using an ID from the provided DOM list."""

        usr_prompt = f"TASK: {task_prompt}\nURL: {current_url}\nSTAGE: {workflow_stage}\n{failure_warning}\n\nINTERACTIVE DOM:\n{interactive_dom}"
        
        time.sleep(1) # Simple rate limit
        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": usr_prompt}],
                temperature=0.1
            )
            text = res.choices[0].message.content.strip()
            return json.loads(text[text.find('{'):text.rfind('}')+1])
        except Exception as e:
            self.logger.error(f"Groq API Error: {e}")
            return None

    def detect_workflow_type(self, task, url): return 'generic_automation'
    def get_workflow_stages(self, type): return ['navigate', 'action', 'extract', 'verify']