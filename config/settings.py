"""
Settings Configuration - Pydantic BaseSettings with Complete YAML Support
Manages all application configuration from environment and YAML
Supports all sections: application, api, browser, anti_bot, proxy, database, 
logging, screenshots, actions, workflows, retry, notifications, security, performance
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import yaml
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application Settings with Complete YAML configuration support"""

    # Tell Pydantic to read from .env file
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # ========================
    # APPLICATION CONFIGURATION
    # ========================
    
    app_name: str = "Enterprise Web Automation Framework"
    app_version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    
    # ========================
    # GEMINI API CONFIGURATION
    # ========================
    
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    vision_model: str = "gemini-2.5-flash"
    computer_use_model: str = "gemini-2.5-computer-use-preview-10-2025"
    groq_api_key: str = ""
    groq_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    openai_api_key: str = ""    # <--- THIS LINE IS CRITICAL
    api_timeout: int = 30
    
    # ========================
    # BROWSER CONFIGURATION
    # ========================
    
    headless: bool = True  # FIXED: Changed from headless_mode to headless
    browser_type: str = "chrome"
    disable_gpu: bool = True
    no_sandbox: bool = True
    disable_dev_shm: bool = True
    
    window_width: int = 1920
    window_height: int = 1080
    viewport_width: int = 1920  # Added for compatibility
    viewport_height: int = 1080  # Added for compatibility
    
    # ========================
    # ANTI-BOT CONFIGURATION
    # ========================
    
    anti_bot_enabled: bool = True  # Added
    enable_stealth: bool = True
    user_agent_rotation: bool = True
    randomize_headers: bool = True
    random_delay: bool = True
    delay_range_min: float = 0.3
    delay_range_max: float = 1.5
    typing_delay_min: float = 0.02
    typing_delay_max: float = 0.08
    
    # ========================
    # PROXY CONFIGURATION
    # ========================
    
    use_proxy: bool = False
    proxy_url: str = ""
    rotate_proxy: bool = False
    proxy_list: List[str] = []
    proxy_list_file: str = "proxies.txt"
    
    # ========================
    # TIMING CONFIGURATION
    # ========================
    
    page_load_timeout: int = 30
    element_wait_timeout: int = 10
    action_delay_min: float = 0.3
    action_delay_max: float = 1.0
    
    # ========================
    # TARGET CONFIGURATION
    # ========================
    
    target_url: str = "https://demoqa.com/"
    chrome_executable_path: Optional[str] = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    firefox_executable_path: Optional[str] = None
    
    # ========================
    # DATABASE CONFIGURATION
    # ========================
    
    database_url: str = "sqlite:///automation.db"
    db_echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_pre_ping: bool = True
    
    # ========================
    # LOGGING CONFIGURATION
    # ========================
    
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "automation.log"
    log_format: str = "detailed"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    
    # Logging Handlers
    log_file_enabled: bool = True
    log_file_level: str = "INFO"
    log_console_enabled: bool = True
    log_console_level: str = "INFO"
    log_syslog_enabled: bool = False
    log_syslog_level: str = "ERROR"
    
    # ========================
    # SCREENSHOT CONFIGURATION
    # ========================
    
    screenshots_enabled: bool = True
    screenshot_dir: str = "screenshots"
    screenshot_path: Path = Path("screenshots")
    full_page_screenshots: bool = True
    screenshot_format: str = "png"
    screenshot_quality: int = 90
    
    # ========================
    # ACTION CONFIGURATION
    # ========================
    
    click_timeout: int = 8000
    click_delay_after: float = 0.1
    
    input_timeout: int = 3000
    input_delay_after: float = 0.05
    
    key_press_timeout: int = 3000
    key_press_delay_after: float = 0.1
    
    navigation_timeout: int = 30000
    navigation_delay_after: float = 0.5
    
    # ========================
    # WORKFLOW CONFIGURATION
    # ========================
    
    form_filling_enabled: bool = True
    form_filling_timeout: int = 120
    form_filling_max_retries: int = 3
    
    scraping_enabled: bool = True
    scraping_timeout: int = 300
    scraping_batch_size: int = 100
    
    interaction_enabled: bool = True
    interaction_timeout: int = 180
    max_actions: int = 50
    
    # ========================
    # RETRY CONFIGURATION
    # ========================
    
    max_retry_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    backoff_jitter: bool = True
    
    # ========================
    # NOTIFICATION CONFIGURATION
    # ========================
    
    notifications_enabled: bool = False
    email_enabled: bool = False
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    
    webhook_enabled: bool = False
    webhook_url: str = ""
    
    # ========================
    # SECURITY CONFIGURATION
    # ========================
    
    verify_ssl: bool = True
    require_authentication: bool = False
    api_key_required: bool = False
    log_sensitive_data: bool = False
    
    # ========================
    # PERFORMANCE CONFIGURATION
    # ========================
    
    parallel_execution: bool = False
    max_concurrent_tasks: int = 1
    memory_limit_mb: int = 512
    cpu_limit_percent: int = 80
    
    def __init__(self, **data):
        """Initialize settings and load YAML config"""
        super().__init__(**data)
        self.load_yaml_config()
    
    def load_yaml_config(self, config_file: str = "config.yaml"):
        """Load and apply YAML configuration if file exists"""
        try:
            config_path = Path(config_file)
            
            if not config_path.exists():
                logger.debug(f"Config file not found: {config_file}")
                return
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                logger.debug("Config file is empty")
                return
            
            # ========================
            # APPLICATION SECTION
            # ========================
            if 'application' in config_data:
                app = config_data['application']
                self.app_name = app.get('name', self.app_name)
                self.app_version = app.get('version', self.app_version)
                self.environment = app.get('environment', self.environment)
                self.debug = app.get('debug', self.debug)
                logger.debug(f"Applied application settings from YAML")
            
            # ========================
            # API SECTION
            # ========================
            if 'api' in config_data:
                api = config_data['api']
                
                if 'gemini' in api:
                    gemini = api['gemini']
                    if 'api_key' in gemini:
                        self.gemini_api_key = gemini['api_key']
                    self.gemini_model = gemini.get('model', self.gemini_model)
                    self.vision_model = gemini.get('vision_model', self.vision_model)
                    self.api_timeout = gemini.get('timeout', self.api_timeout)
                    logger.debug(f"Applied Gemini API settings from YAML")
                
                if 'groq' in api:
                    groq = api['groq']
                    if 'api_key' in groq:
                        self.groq_api_key = groq['api_key']
                    self.groq_model = groq.get('model', self.groq_model)
                    logger.debug(f"Applied Groq API settings from YAML")
            
            # ========================
            # BROWSER SECTION
            # ========================
            if 'browser' in config_data:
                browser = config_data['browser']
                self.headless = browser.get('headless', self.headless)
                self.browser_type = browser.get('type', self.browser_type)
                self.disable_gpu = browser.get('disable_gpu', self.disable_gpu)
                self.no_sandbox = browser.get('no_sandbox', self.no_sandbox)
                self.disable_dev_shm = browser.get('disable_dev_shm', self.disable_dev_shm)
                
                if 'window' in browser:
                    window = browser['window']
                    self.window_width = window.get('width', self.window_width)
                    self.window_height = window.get('height', self.window_height)
                    self.viewport_width = window.get('width', self.viewport_width)
                    self.viewport_height = window.get('height', self.viewport_height)
                
                logger.debug(f"Applied browser settings from YAML")
            
            # ========================
            # ANTI-BOT SECTION
            # ========================
            if 'anti_bot' in config_data:
                anti_bot = config_data['anti_bot']
                self.anti_bot_enabled = anti_bot.get('enabled', self.anti_bot_enabled)
                self.enable_stealth = anti_bot.get('stealth', self.enable_stealth)
                self.user_agent_rotation = anti_bot.get('user_agent_rotation', self.user_agent_rotation)
                self.randomize_headers = anti_bot.get('randomize_headers', self.randomize_headers)
                self.random_delay = anti_bot.get('random_delay', self.random_delay)
                
                if 'delays' in anti_bot:
                    delays = anti_bot['delays']
                    self.delay_range_min = delays.get('min', self.delay_range_min)
                    self.delay_range_max = delays.get('max', self.delay_range_max)
                    self.typing_delay_min = delays.get('typing_min', self.typing_delay_min)
                    self.typing_delay_max = delays.get('typing_max', self.typing_delay_max)
                
                logger.debug(f"Applied anti-bot settings from YAML")
            
            # ========================
            # PROXY SECTION
            # ========================
            if 'proxy' in config_data:
                proxy = config_data['proxy']
                self.use_proxy = proxy.get('enabled', self.use_proxy)
                self.proxy_url = proxy.get('url', self.proxy_url)
                self.rotate_proxy = proxy.get('rotate', self.rotate_proxy)
                
                if 'list' in proxy:
                    self.proxy_list = proxy['list']
                
                self.proxy_list_file = proxy.get('list_file', self.proxy_list_file)
                logger.debug(f"Applied proxy settings from YAML")
            
            # ========================
            # TIMING SECTION
            # ========================
            if 'timeouts' in config_data:
                timeouts = config_data['timeouts']
                self.page_load_timeout = timeouts.get('page_load', self.page_load_timeout)
                self.element_wait_timeout = timeouts.get('element_wait', self.element_wait_timeout)
                
                if 'actions' in timeouts:
                    actions = timeouts['actions']
                    self.action_delay_min = actions.get('min', self.action_delay_min)
                    self.action_delay_max = actions.get('max', self.action_delay_max)
                
                logger.debug(f"Applied timeout settings from YAML")
            
            # ========================
            # DATABASE SECTION
            # ========================
            if 'database' in config_data:
                db = config_data['database']
                self.database_url = db.get('url', self.database_url)
                self.db_echo = db.get('echo', self.db_echo)
                self.pool_size = db.get('pool_size', self.pool_size)
                self.max_overflow = db.get('max_overflow', self.max_overflow)
                logger.debug(f"Applied database settings from YAML")
            
            # ========================
            # LOGGING SECTION
            # ========================
            if 'logging' in config_data:
                logging_cfg = config_data['logging']
                self.log_level = logging_cfg.get('level', self.log_level)
                self.log_dir = logging_cfg.get('directory', self.log_dir)
                self.log_format = logging_cfg.get('format', self.log_format)
                self.max_bytes = logging_cfg.get('max_bytes', self.max_bytes)
                self.backup_count = logging_cfg.get('backup_count', self.backup_count)
                
                # Handlers
                if 'handlers' in logging_cfg:
                    handlers = logging_cfg['handlers']
                    
                    if 'file' in handlers:
                        file_cfg = handlers['file']
                        self.log_file_enabled = file_cfg.get('enabled', self.log_file_enabled)
                        self.log_file_level = file_cfg.get('level', self.log_file_level)
                    
                    if 'console' in handlers:
                        console_cfg = handlers['console']
                        self.log_console_enabled = console_cfg.get('enabled', self.log_console_enabled)
                        self.log_console_level = console_cfg.get('level', self.log_console_level)
                    
                    if 'syslog' in handlers:
                        syslog_cfg = handlers['syslog']
                        self.log_syslog_enabled = syslog_cfg.get('enabled', self.log_syslog_enabled)
                        self.log_syslog_level = syslog_cfg.get('level', self.log_syslog_level)
                
                logger.debug(f"Applied logging settings from YAML")
            
            # ========================
            # SCREENSHOTS SECTION
            # ========================
            if 'screenshots' in config_data:
                ss = config_data['screenshots']
                self.screenshots_enabled = ss.get('enabled', self.screenshots_enabled)
                self.screenshot_dir = ss.get('directory', self.screenshot_dir)
                self.full_page_screenshots = ss.get('full_page', self.full_page_screenshots)
                self.screenshot_format = ss.get('format', self.screenshot_format)
                self.screenshot_quality = ss.get('quality', self.screenshot_quality)
                logger.debug(f"Applied screenshot settings from YAML")
            
            # ========================
            # ACTIONS SECTION
            # ========================
            if 'actions' in config_data:
                actions = config_data['actions']
                
                if 'click' in actions:
                    click_cfg = actions['click']
                    self.click_timeout = click_cfg.get('timeout', self.click_timeout)
                    self.click_delay_after = click_cfg.get('delay_after', self.click_delay_after)
                
                if 'input' in actions:
                    input_cfg = actions['input']
                    self.input_timeout = input_cfg.get('timeout', self.input_timeout)
                    self.input_delay_after = input_cfg.get('delay_after', self.input_delay_after)
                
                if 'key_press' in actions:
                    key_cfg = actions['key_press']
                    self.key_press_timeout = key_cfg.get('timeout', self.key_press_timeout)
                    self.key_press_delay_after = key_cfg.get('delay_after', self.key_press_delay_after)
                
                if 'navigation' in actions:
                    nav_cfg = actions['navigation']
                    self.navigation_timeout = nav_cfg.get('timeout', self.navigation_timeout)
                    self.navigation_delay_after = nav_cfg.get('delay_after', self.navigation_delay_after)
                
                logger.debug(f"Applied action settings from YAML")
            
            # ========================
            # WORKFLOWS SECTION
            # ========================
            if 'workflows' in config_data:
                workflows = config_data['workflows']
                
                if 'form_filling' in workflows:
                    ff = workflows['form_filling']
                    self.form_filling_enabled = ff.get('enabled', self.form_filling_enabled)
                    self.form_filling_timeout = ff.get('timeout', self.form_filling_timeout)
                    self.form_filling_max_retries = ff.get('max_retries', self.form_filling_max_retries)
                
                if 'scraping' in workflows:
                    scraping = workflows['scraping']
                    self.scraping_enabled = scraping.get('enabled', self.scraping_enabled)
                    self.scraping_timeout = scraping.get('timeout', self.scraping_timeout)
                    self.scraping_batch_size = scraping.get('batch_size', self.scraping_batch_size)
                
                if 'interaction' in workflows:
                    interaction = workflows['interaction']
                    self.interaction_enabled = interaction.get('enabled', self.interaction_enabled)
                    self.interaction_timeout = interaction.get('timeout', self.interaction_timeout)
                    self.max_actions = interaction.get('max_actions', self.max_actions)
                
                logger.debug(f"Applied workflow settings from YAML")
            
            # ========================
            # RETRY SECTION
            # ========================
            if 'retry' in config_data:
                retry = config_data['retry']
                self.max_retry_attempts = retry.get('max_attempts', self.max_retry_attempts)
                self.initial_delay = retry.get('initial_delay', self.initial_delay)
                self.max_delay = retry.get('max_delay', self.max_delay)
                self.backoff_factor = retry.get('backoff_factor', self.backoff_factor)
                self.backoff_jitter = retry.get('backoff_jitter', self.backoff_jitter)
                logger.debug(f"Applied retry settings from YAML")
            
            # ========================
            # NOTIFICATIONS SECTION
            # ========================
            if 'notifications' in config_data:
                notif = config_data['notifications']
                self.notifications_enabled = notif.get('enabled', self.notifications_enabled)
                
                if 'email' in notif:
                    email_cfg = notif['email']
                    self.email_enabled = email_cfg.get('enabled', self.email_enabled)
                    self.email_smtp_server = email_cfg.get('smtp_server', self.email_smtp_server)
                    self.email_smtp_port = email_cfg.get('smtp_port', self.email_smtp_port)
                
                if 'slack' in notif:
                    slack_cfg = notif['slack']
                    self.slack_enabled = slack_cfg.get('enabled', self.slack_enabled)
                    self.slack_webhook_url = slack_cfg.get('webhook_url', self.slack_webhook_url)
                
                if 'webhook' in notif:
                    webhook_cfg = notif['webhook']
                    self.webhook_enabled = webhook_cfg.get('enabled', self.webhook_enabled)
                    self.webhook_url = webhook_cfg.get('url', self.webhook_url)
                
                logger.debug(f"Applied notification settings from YAML")
            
            # ========================
            # SECURITY SECTION
            # ========================
            if 'security' in config_data:
                security = config_data['security']
                self.verify_ssl = security.get('verify_ssl', self.verify_ssl)
                self.require_authentication = security.get('require_authentication', self.require_authentication)
                self.api_key_required = security.get('api_key_required', self.api_key_required)
                self.log_sensitive_data = security.get('log_sensitive_data', self.log_sensitive_data)
                logger.debug(f"Applied security settings from YAML")
            
            # ========================
            # PERFORMANCE SECTION
            # ========================
            if 'performance' in config_data:
                perf = config_data['performance']
                self.parallel_execution = perf.get('parallel_execution', self.parallel_execution)
                self.max_concurrent_tasks = perf.get('max_concurrent_tasks', self.max_concurrent_tasks)
                self.memory_limit_mb = perf.get('memory_limit_mb', self.memory_limit_mb)
                self.cpu_limit_percent = perf.get('cpu_limit_percent', self.cpu_limit_percent)
                logger.debug(f"Applied performance settings from YAML")
            
            logger.info("All YAML configuration sections applied successfully")
        
        except Exception as e:
            logger.warning(f"Error applying YAML config: {e}")
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get complete logging configuration"""
        return {
            'level': self.log_level,
            'format': self.log_format,
            'directory': self.log_dir,
            'handlers': {
                'file': {
                    'enabled': self.log_file_enabled,
                    'level': self.log_file_level
                },
                'console': {
                    'enabled': self.log_console_enabled,
                    'level': self.log_console_level
                },
                'syslog': {
                    'enabled': self.log_syslog_enabled,
                    'level': self.log_syslog_level
                }
            }
        }
    
    def get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Get specific workflow configuration"""
        workflows = {
            'form_filling': {
                'enabled': self.form_filling_enabled,
                'timeout': self.form_filling_timeout,
                'max_retries': self.form_filling_max_retries
            },
            'scraping': {
                'enabled': self.scraping_enabled,
                'timeout': self.scraping_timeout,
                'batch_size': self.scraping_batch_size
            },
            'interaction': {
                'enabled': self.interaction_enabled,
                'timeout': self.interaction_timeout,
                'max_actions': self.max_actions
            }
        }
        return workflows.get(workflow_name, {})


# Initialize settings
settings = Settings()