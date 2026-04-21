"""
Computer Use Loop - PRODUCTION READY (OpenAI Fallback)
Main orchestration engine with DOM Distillation and AI Self-Correction
"""

import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from logging_config.logger import get_logger
from project.groq_automation_engine import GroqAutomationEngine
from project.openai_automation_engine import OpenAIAutomationEngine
from project.action_executor_enhanced import ActionExecutor

class ComputerUseLoop:
    def __init__(self, driver, anti_bot_service=None):
        self.logger = get_logger(self.__class__.__name__)
        self.driver = driver
        self.anti_bot_service = anti_bot_service
        
        self.groq_engine = GroqAutomationEngine()
        self.openai_engine = OpenAIAutomationEngine()
        self.action_executor = ActionExecutor(driver, anti_bot_service)
        
        self.iteration = 0
        self.executed_actions = 0
        self.visited_urls = set()
        self.workflow_history = []
    
    def _get_interactive_dom(self) -> str:
        """Injects JS to tag clickable elements so AI doesn't have to guess CSS"""
        js_script = """
        try {
            let interactives = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]');
            let simplifiedDom = [];
            let idCounter = 1;
            interactives.forEach(el => {
                let rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden') {
                    let tagId = 'bot-id-' + idCounter++;
                    el.setAttribute('data-bot-id', tagId);
                    let text = el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '';
                    text = text.replace(/\\n/g, ' ').substring(0, 80).trim();
                    if(text || el.tagName.toLowerCase() === 'input') {
                        simplifiedDom.push(`[ID: ${tagId}] <${el.tagName.toLowerCase()}> ${text}`);
                    }
                }
            });
            return simplifiedDom.join('\\n');
        } catch(e) { return "Error generating DOM"; }
        """
        try:
            return self.driver.execute_script(js_script)
        except Exception as e:
            self.logger.warning(f"DOM tagging failed: {e}")
            return "HTML Extraction Failed"
    
    def execute_automation(self, task_prompt: str, target_url: Optional[str] = None, max_iterations: int = 25) -> Dict[str, Any]:
        self.logger.info("\n" + "="*100)
        self.logger.info("🤖 AGENTIC COMPUTER USE LOOP STARTED")
        self.logger.info("="*100)
        
        start_time = datetime.now()
        workflow_type = "generic_automation"
        
        try:
            if target_url:
                self.logger.info(f"[NAVIGATE] {target_url}")
                self.driver.get(target_url)
                time.sleep(3)
            
            current_url = self.driver.current_url
            workflow_type = self.groq_engine.detect_workflow_type(task_prompt, current_url)
            workflow_stages = self.groq_engine.get_workflow_stages(workflow_type)
            current_stage_idx = 0
            
            for self.iteration in range(1, max_iterations + 1):
                if current_stage_idx >= len(workflow_stages):
                    break
                    
                current_stage = workflow_stages[current_stage_idx]
                self.logger.info(f"\n[ITERATION {self.iteration}] Stage: {current_stage}")
                
                # 1. Distill DOM
                interactive_dom = self._get_interactive_dom()
                current_url = self.driver.current_url
                self.visited_urls.add(current_url)
                
                # 2. Check for AI Loops
                force_fallback = False
                recent_failures = []
                if len(self.workflow_history) >= 2:
                    if not self.workflow_history[-1]['success'] and not self.workflow_history[-2]['success']:
                        self.logger.warning("🔄 [LOOP DETECTED] AI failed twice. Routing to OpenAI...")
                        force_fallback = True
                
                for entry in reversed(self.workflow_history[-3:]):
                    if not entry.get('success'):
                        recent_failures.append(f"{entry.get('action')} on '{entry.get('target')}'")
                    else: break
                
                # 3. Analyze
                analysis = self._analyze_page(interactive_dom, task_prompt, current_url, self.iteration, current_stage, force_fallback, recent_failures)
                
                if not analysis:
                    self.logger.error("❌ Analysis returned None. Breaking loop.")
                    break
                    
                self._log_analysis(analysis)
                
                # 4. Execute
                success = self._execute_action(analysis)
                if success: self.executed_actions += 1
                
                self.workflow_history.append({
                    'iteration': self.iteration, 'stage': current_stage,
                    'action': analysis.get('action_type'), 'target': analysis.get('target'), 'success': success
                })
                
                if analysis.get('stage_complete') and success:
                    current_stage_idx += 1
                if analysis.get('task_complete') and success:
                    self.logger.info("✅ [TASK COMPLETE]")
                    break
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"[FATAL] Workflow crashed: {e}")
            
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            'task_prompt': task_prompt, 'workflow_type': workflow_type,
            'total_iterations': self.iteration, 'total_actions': self.executed_actions,
            'visited_urls': list(self.visited_urls), 'execution_time': execution_time,
            'groq_used': True, 'fallback_used': True, 'workflow_history': self.workflow_history
        }

    def _analyze_page(self, interactive_dom: str, task_prompt: str, current_url: str, iteration: int, workflow_stage: str, force_fallback: bool, recent_failures: list) -> Dict:
        if self.groq_engine.groq_available and not force_fallback:
            try:
                analysis = self.groq_engine.analyze_with_structured_prompt(interactive_dom, task_prompt, current_url, iteration, workflow_stage, recent_failures)
                if analysis and 'action_type' in analysis:
                    return analysis
            except Exception as e:
                self.logger.warning(f"⚡ Groq Failed: {e}. Falling back to OpenAI.")
                
        return self.openai_engine.analyze_page_with_openai(interactive_dom, task_prompt, current_url, iteration, workflow_stage, recent_failures)

    def _execute_action(self, analysis: Dict[str, Any]) -> bool:
        action = analysis.get('action_type')
        target = analysis.get('target', '')
        val = analysis.get('value', '')
        
        if action == 'click': return self.action_executor.click_element_indestructible(target)
        elif action in ['fill', 'search']: return self.action_executor.fill_input(target, val)
        elif action == 'navigate': return self.action_executor.navigate(target)
        elif action == 'scroll': return self.action_executor.scroll_page(amount=3)
        elif action == 'wait': return self.action_executor.wait_for_element(target)
        elif action == 'extract': return True
        return False

    def _log_analysis(self, analysis: Dict):
        self.logger.info(f"👉 [DECISION] {analysis.get('action_type')} -> {analysis.get('target')}")
        self.logger.info(f"💡 [REASON] {analysis.get('reasoning')}")