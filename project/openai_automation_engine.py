"""
OpenAI Automation Engine - PRODUCTION READY
"""
import json
import os
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# FORCE LOAD .ENV VARIABLES
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️ The 'openai' package is not installed. Run: pip install openai")
    OPENAI_AVAILABLE = False
    
try:
    from logging_config.logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)

class OpenAIAutomationEngine:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.openai_available = False
        self.client = None
        self.model = "gpt-4o"
        
        if OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.openai_available = True
                self.logger.info(f"✅ OpenAI Fallback initialized ({self.model})")
            else:
                self.logger.error("❌ [OPENAI] API key not found! Please check your .env file.")

    def analyze_page_with_openai(self, interactive_dom: str, task_prompt: str, current_url: str, iteration: int, workflow_stage: str, recent_failures: list = None) -> Dict[str, Any]:
        if not self.openai_available:
            self.logger.error("[OPENAI] Cannot execute: API key missing. Falling back to safe scroll.")
            return self._safe_fallback_action()
        
        try:
            failure_warning = ""
            if recent_failures:
                failure_warning = "\n⚠️ CRITICAL - PREVIOUS ACTIONS FAILED:\n"
                for failure in recent_failures:
                    failure_warning += f"- DO NOT TRY: {failure}. Find an alternative target or strategy.\n"

            system_prompt = """You are an elite web automation agent taking over because the fast-agent failed.
Look at the INTERACTIVE DOM list. It contains all visible elements tagged with [ID: bot-id-X].
Determine the correct next action to progress the task.
Return ONLY valid JSON:
{
    "analysis": "Briefly explain what you see and what must be done",
    "action_type": "click|fill|search|scroll|navigate|extract|wait",
    "target": "[data-bot-id='bot-id-X']", 
    "value": "text to type or null",
    "reasoning": "Why this fixes the blockage",
    "stage_complete": false,
    "task_complete": false
}
CRITICAL: For targets, ALWAYS use the CSS selector format: [data-bot-id='bot-id-X']"""
            
            user_prompt = f"""TASK: {task_prompt}
URL: {current_url}
STAGE: {workflow_stage}
{failure_warning}

INTERACTIVE DOM (Cleaned elements):
{interactive_dom}"""
            
            self.logger.info("[OPENAI] 🧠 Heavy reasoning invoked...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"[OPENAI] Analysis failed: {e}")
            return self._safe_fallback_action()

    def _safe_fallback_action(self) -> Dict[str, Any]:
        return {
            'analysis': 'All AI engines failed.',
            'action_type': 'scroll',
            'target': 'down',
            'value': 3,
            'reasoning': 'Scrolling to trigger new DOM elements.',
            'stage_complete': False,
            'task_complete': False
        }