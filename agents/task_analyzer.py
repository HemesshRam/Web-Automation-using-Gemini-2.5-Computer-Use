"""Task Analyzer Agent - Complete Version"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.settings import settings
from logging_config.logger import get_logger

logger = get_logger(__name__)


class TaskPromptLibrary:
    """Pre-configured task prompts"""

    DEMOQA_TASKS = {
        'full_demoqa': {
            'name': 'Full DemoQA Intelligence Extraction',
            'prompt': 'From https://demoqa.com/, explore and document all interactive testing modules (Elements, Forms, Alerts, Widgets, Interactions, BookStore). Extract complete automation intelligence including element selectors, form validations, dynamic behaviors, and interaction patterns. Generate comprehensive intelligence report with screenshots and structured data for automation framework development.',
            'target_url': 'https://demoqa.com/',
            'expected_duration': 600,
            'requires_form_interaction': True,
            'requires_data_extraction': True
        }
    }

    @classmethod
    def get_task(cls, task_name: str) -> Optional[Dict]:
        return cls.DEMOQA_TASKS.get(task_name)

    @classmethod
    def list_tasks(cls) -> Dict:
        return {k: {'name': v['name'], 'duration': v['expected_duration']} 
                for k, v in cls.DEMOQA_TASKS.items()}

    @classmethod
    def get_task_prompt(cls, task_name: str) -> Optional[str]:
        task = cls.get_task(task_name)
        return task['prompt'] if task else None

    @classmethod
    def get_task_url(cls, task_name: str) -> Optional[str]:
        task = cls.get_task(task_name)
        return task['target_url'] if task else None


class TaskAnalyzer:
    """Analyzes task prompts and creates execution plans"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("TaskAnalyzer initialized")

    def analyze_task(self, task_prompt: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"Analyzing task: {task_prompt[:100]}...")

            intent = self._classify_intent(task_prompt)
            self.logger.info(f"Classified intent: {intent['primary_action']}")

            sub_tasks = self._generate_subtasks(task_prompt, intent)
            self.logger.info(f"Generated {len(sub_tasks)} sub-tasks")

            execution_plan = {
                'task_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
                'task_prompt': task_prompt,
                'intent': intent,
                'sub_tasks': sub_tasks,
                'total_steps': len(sub_tasks),
                'estimated_timeout': sum(t.get('timeout', 10) for t in sub_tasks),
                'target_url': str(settings.target_url),
                'status': 'planned',
                'created_at': datetime.now().isoformat()
            }

            return execution_plan

        except Exception as e:
            self.logger.error(f"Task analysis failed: {str(e)}")
            return {'error': str(e), 'task_prompt': task_prompt, 'status': 'analysis_failed'}

    def _classify_intent(self, task_prompt: str) -> Dict[str, Any]:
        prompt_lower = task_prompt.lower()

        action_keywords = {
            'explore': ['explore', 'discover', 'find', 'all', 'comprehensive'],
            'extract': ['extract', 'scrape', 'collect', 'gather', 'document', 'intelligence'],
            'fill_form': ['fill', 'submit', 'form', 'input', 'login'],
            'click': ['click', 'press', 'tap', 'select'],
        }

        primary_action = 'explore'
        matched_keywords = []

        for action, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    primary_action = action
                    matched_keywords.append(keyword)

        requires_form_interaction = any(kw in prompt_lower for kw in ['fill', 'submit', 'form', 'input'])
        requires_data_extraction = any(kw in prompt_lower for kw in ['extract', 'scrape', 'collect', 'document', 'intelligence'])

        return {
            'primary_action': primary_action,
            'matched_keywords': matched_keywords,
            'requires_form_interaction': requires_form_interaction,
            'requires_data_extraction': requires_data_extraction,
            'confidence': min(len(matched_keywords) * 0.3, 1.0) if matched_keywords else 0.5,
            'raw_prompt': task_prompt
        }

    def _generate_subtasks(self, task_prompt: str, intent: Dict) -> List[Dict[str, Any]]:
        sub_tasks = []

        sub_tasks.append({
            'order': 1,
            'action': 'screenshot',
            'description': 'Capture initial homepage',
            'required': True,
            'timeout': 10
        })

        sub_tasks.append({
            'order': 2,
            'action': 'extract_data',
            'description': 'Extract initial page structure',
            'required': False,
            'timeout': 15
        })

        sub_tasks.append({
            'order': 3,
            'action': 'explore_all_pages',
            'description': 'Navigate and explore ALL modules and sub-pages on website',
            'required': True,
            'timeout': 300
        })

        if intent['requires_form_interaction']:
            sub_tasks.append({
                'order': 4,
                'action': 'interact_forms',
                'description': 'Identify and interact with forms',
                'required': False,
                'timeout': 60
            })

        if intent['requires_data_extraction']:
            sub_tasks.append({
                'order': 5,
                'action': 'extract_comprehensive_data',
                'description': 'Extract selectors, validations, behaviors from all pages',
                'required': True,
                'timeout': 120
            })

        sub_tasks.append({
            'order': len(sub_tasks) + 1,
            'action': 'generate_report',
            'description': 'Generate intelligence report with findings',
            'required': True,
            'timeout': 30
        })

        return sub_tasks