"""
Main Entry Point
Uses Computer Use Loop with Groq + Fallback Analysis
Supports Amazon, Yahoo Finance, YouTube, DemoQA, and Custom Workflows
"""

import sys
import time
import os
from pathlib import Path
from datetime import datetime

# Use absolute module imports to keep the IDE and Python runtime structurally happy without sys.path hacks.
try:
    from config.settings import settings
    from logging_config.logger import configure_logging, get_logger
    from selenium_driver.driver_factory import DriverFactory
    from detectors.anti_bot_service import AntiBotService
    from project.computer_use_loop import ComputerUseLoop
    from persistence.repository import TaskRepository
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure all required modules are installed")
    sys.exit(1)

logger = None


def initialize_application():
    """Initialize application"""
    
    global logger
    
    try:
        configure_logging()
    except:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    logger = get_logger(__name__)
    
    logger.info("\n" + "="*150)
    logger.info("🚀 WEB AUTOMATION - GROQ + FALLBACK ANALYSIS (NO GEMINI)")
    logger.info("="*150 + "\n")
    
    # Configuration info
    try:
        logger.info(f"[CONFIG] Browser: Chrome")
        logger.info(f"[CONFIG] Headless: {settings.headless if hasattr(settings, 'headless') else 'Default'}")
        logger.info(f"[CONFIG] Anti-Bot: Enabled")
        logger.info(f"[GROQ] Model: meta-llama/llama-4-scout-17b-16e-instruct")
        logger.info(f"[FALLBACK] Rule-Based Analysis: Enabled\n")
    except:
        logger.info("[CONFIG] Default settings loaded\n")


def display_main_menu():
    """Display main menu"""
    
    print("\n" + "="*150)
    print("🎯 WEB AUTOMATION MENU")
    print("="*150)
    print("\n1. Automated Amazon Search (Search for products, extract variants & pricing)")
    print("2. Automated Yahoo Finance (Search stocks, extract prices)")
    print("3. Automated YouTube (Search videos, click and extract info)")
    print("4. Automated DemoQA (Explore all modules: Elements, Forms, Alerts, Widgets, BookStore)")
    print("5. Custom Website Automation (Enter your own workflow)")
    print("6. View Settings")
    print("7. Exit")
    print("\n" + "="*150)


def run_amazon_automation():
    """Run Amazon search automation"""
    
    driver = None
    
    try:
        print("\n" + "="*150)
        print("🛒 AMAZON AUTOMATION - Search Products")
        print("="*150)
        
        # Get search term
        search_term = input("\nEnter product to search (default: iPhone 17 Pro): ").strip()
        if not search_term:
            search_term = "iPhone 17 Pro"
        
        task_prompt = f"Go to amazon.com, search for {search_term}, extract all variants, pricing, and provide summary"
        
        logger.info(f"\n[TASK] {task_prompt}")
        logger.info("[BROWSER] Initializing...")
        
        # Initialize driver
        driver_factory = DriverFactory()
        anti_bot = AntiBotService()
        anti_bot.apply_stealth_measures()
        
        driver = driver_factory.create_driver("chrome")
        logger.info("[BROWSER] Ready\n")
        
        # Execute automation
        computer_loop = ComputerUseLoop(driver, anti_bot)
        results = computer_loop.execute_automation(
            task_prompt,
            target_url="https://amazon.com",
            max_iterations=25
        )
        
        _display_results(results)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPT] User interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if driver:
            logger.info("[BROWSER] Closing...")
            time.sleep(10)  # Let user see results
            driver.quit()


def run_yahoo_finance_automation():
    """Run Yahoo Finance stock automation"""
    
    driver = None
    
    try:
        print("\n" + "="*150)
        print("📈 YAHOO FINANCE AUTOMATION - Stock Search")
        print("="*150)
        
        # Get stock symbol
        stock = input("\nEnter stock symbol (default: TESLA): ").strip().upper()
        if not stock:
            stock = "TESLA"
        
        task_prompt = f"Go to finance.yahoo.com, search for {stock} stock, extract current price and provide summary"
        
        logger.info(f"\n[TASK] {task_prompt}")
        logger.info("[BROWSER] Initializing...")
        
        # Initialize driver
        driver_factory = DriverFactory()
        anti_bot = AntiBotService()
        anti_bot.apply_stealth_measures()
        
        driver = driver_factory.create_driver("chrome")
        logger.info("[BROWSER] Ready\n")
        
        # Execute automation
        computer_loop = ComputerUseLoop(driver, anti_bot)
        results = computer_loop.execute_automation(
            task_prompt,
            target_url="https://finance.yahoo.com",
            max_iterations=20
        )
        
        _display_results(results)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPT] User interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if driver:
            logger.info("[BROWSER] Closing...")
            time.sleep(10)
            driver.quit()


def run_youtube_automation():
    """Run YouTube search automation"""
    
    driver = None
    
    try:
        print("\n" + "="*150)
        print("▶️ YOUTUBE AUTOMATION - Search & Watch")
        print("="*150)
        
        # Get search term
        search_term = input("\nEnter video to search (default: AR Rahman songs): ").strip()
        if not search_term:
            search_term = "AR Rahman songs"
        
        task_prompt = f"Go to youtube.com, search for {search_term}, click first video, extract title and description, provide summary"
        
        logger.info(f"\n[TASK] {task_prompt}")
        logger.info("[BROWSER] Initializing...")
        
        # Initialize driver
        driver_factory = DriverFactory()
        anti_bot = AntiBotService()
        anti_bot.apply_stealth_measures()
        
        driver = driver_factory.create_driver("chrome")
        logger.info("[BROWSER] Ready\n")
        
        # Execute automation
        computer_loop = ComputerUseLoop(driver, anti_bot)
        results = computer_loop.execute_automation(
            task_prompt,
            target_url="https://youtube.com",
            max_iterations=25
        )
        
        _display_results(results)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPT] User interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if driver:
            logger.info("[BROWSER] Closing...")
            time.sleep(10)
            driver.quit()


def run_demoqa_automation():
    """Run DemoQA full exploration"""
    
    driver = None
    
    try:
        print("\n" + "="*150)
        print("🧪 DEMOQA AUTOMATION - Full Exploration")
        print("="*150)
        
        task_prompt = """Explore DemoQA site and visit all modules in order:
1. Elements
2. Forms
3. Alerts
4. Widgets
5. Interactions
6. BookStore

Extract key information from each module and provide a complete summary."""
        
        logger.info(f"\n[TASK] Full DemoQA Exploration")
        logger.info("[BROWSER] Initializing...")
        
        # Initialize driver
        driver_factory = DriverFactory()
        anti_bot = AntiBotService()
        anti_bot.apply_stealth_measures()
        
        driver = driver_factory.create_driver("chrome")
        logger.info("[BROWSER] Ready\n")
        
        # Execute automation
        computer_loop = ComputerUseLoop(driver, anti_bot)
        results = computer_loop.execute_automation(
            task_prompt,
            target_url="https://demoqa.com",
            max_iterations=40
        )
        
        _display_results(results)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPT] User interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if driver:
            logger.info("[BROWSER] Closing...")
            time.sleep(10)
            driver.quit()


def run_custom_automation():
    """Run custom website automation"""
    
    driver = None
    
    try:
        print("\n" + "="*150)
        print("🎯 CUSTOM WEBSITE AUTOMATION")
        print("="*150)
        
        print("\nEnter your automation task:")
        print("Examples:")
        print("  - Go to google.com and search for 'Python programming'")
        print("  - Navigate to github.com and search for 'machine learning projects'")
        print("  - Visit flipkart.com and search for 'laptop' and extract prices")
        
        task_prompt = input("\nEnter your task: ").strip()
        
        if not task_prompt or len(task_prompt) < 10:
            logger.warning("[TASK] Invalid task")
            return
        
        logger.info(f"\n[TASK] {task_prompt}")
        logger.info("[BROWSER] Initializing...")
        
        # Initialize driver
        driver_factory = DriverFactory()
        anti_bot = AntiBotService()
        anti_bot.apply_stealth_measures()
        
        driver = driver_factory.create_driver("chrome")
        logger.info("[BROWSER] Ready\n")
        
        # Execute automation
        computer_loop = ComputerUseLoop(driver, anti_bot)
        results = computer_loop.execute_automation(
            task_prompt,
            max_iterations=30
        )
        
        _display_results(results)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPT] User interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if driver:
            logger.info("[BROWSER] Closing...")
            time.sleep(10)
            driver.quit()


def view_settings():
    """Display current settings"""
    
    logger.info("\n" + "="*150)
    logger.info("⚙️ CURRENT SETTINGS")
    logger.info("="*150)
    
    # Safely fetch keys from Pydantic settings
    groq_key = getattr(settings, 'groq_api_key', '') or os.environ.get('GROQ_API_KEY', '')
    openai_key = getattr(settings, 'openai_api_key', '') or os.environ.get('OPENAI_API_KEY', '')
    
    logger.info("\n[GROQ]")
    logger.info(f"  Status: {'✓ Available' if groq_key else '✗ Not configured'}")
    logger.info(f"  Model: {getattr(settings, 'groq_model', 'meta-llama')}")
    if groq_key:
        logger.info(f"  API Key: {groq_key[:8]}...{groq_key[-4:]}")
    else:
        logger.info("  API Key: NOT SET")
        
    logger.info("\n[OPENAI FALLBACK]")
    logger.info(f"  Status: {'✓ Available' if openai_key else '✗ Not configured'}")
    if openai_key:
        logger.info(f"  API Key: {openai_key[:8]}...{openai_key[-4:]}")
    else:
        logger.info("  API Key: NOT SET")
    
    logger.info("\n[ANTI-BOT]")
    logger.info(f"  Stealth Mode: ✓ Enabled")
    logger.info(f"  User Agent Rotation: ✓ Enabled")
    logger.info(f"  Random Delays: ✓ Enabled")
    
    logger.info("\n[WORKFLOWS]")
    logger.info(f"  Amazon Search: ✓")
    logger.info(f"  Yahoo Finance: ✓")
    logger.info(f"  YouTube Search: ✓")
    logger.info(f"  DemoQA Exploration: ✓")
    logger.info(f"  Custom Automation: ✓")
    
    logger.info("\n" + "="*150 + "\n")


def _display_results(results: dict):
    """Display execution results"""
    
    logger.info("\n" + "="*150)
    logger.info("📊 EXECUTION SUMMARY")
    logger.info("="*150)
    
    logger.info(f"\nWorkflow Type: {results.get('workflow_type', 'N/A')}")
    logger.info(f"Total Iterations: {results.get('total_iterations', 0)}")
    logger.info(f"Actions Executed: {results.get('total_actions', 0)}")
    logger.info(f"Pages Visited: {len(results.get('visited_urls', []))}")
    logger.info(f"Execution Time: {results.get('execution_time', 0):.1f}s")
    
    logger.info(f"\n[ENGINES]")
    logger.info(f"  Groq Used: {'✓' if results.get('groq_used') else '✗'}")
    logger.info(f"  Fallback Used: {'✓' if results.get('fallback_used') else '✗'}")
    
    if results.get('visited_urls'):
        logger.info(f"\n[PAGES VISITED]")
        for i, url in enumerate(results['visited_urls'][:5], 1):
            logger.info(f"  {i}. {url[:80]}...")
    
    logger.info("\n" + "="*150 + "\n")


def main():
    """Main application loop"""
    
    try:
        initialize_application()
        
        while True:
            try:
                display_main_menu()
                
                choice = input("\n👉 Enter choice (1-7): ").strip()
                
                if choice == "1":
                    run_amazon_automation()
                
                elif choice == "2":
                    run_yahoo_finance_automation()
                
                elif choice == "3":
                    run_youtube_automation()
                
                elif choice == "4":
                    run_demoqa_automation()
                
                elif choice == "5":
                    run_custom_automation()
                
                elif choice == "6":
                    view_settings()
                
                elif choice == "7":
                    logger.info("[EXIT] Goodbye! 👋")
                    break
                
                else:
                    logger.warning("[INPUT] Invalid choice (1-7)")
                
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                logger.info("[INTERRUPT] Exiting...")
                break
            
            except Exception as e:
                logger.error(f"[ERROR] {str(e)}")
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()