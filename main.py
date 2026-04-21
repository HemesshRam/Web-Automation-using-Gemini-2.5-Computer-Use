"""
Main Entry Point - Gemini 2.5 Computer Use Real Website Automation
Supports: Amazon, YouTube, MakeMyTrip, Yahoo Finance, GitHub, Booking, Flipkart, Alibaba, etc.
Enhanced with intelligent fallback analysis and website-specific workflows
Powered by Gemini 2.5 Computer Use model with Groq + Rule-Based fallback
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

from config.settings import settings
from logging_config.logger import configure_logging, get_logger
from core.automation_engine import AutomationEngine
from persistence.database import init_db

logger = None


def initialize_application():
    """Initialize application with proper error handling"""
    
    global logger
    
    configure_logging()
    logger = get_logger(__name__)
    
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init: {e}")
    
    logger.info("\n" + "="*150)
    logger.info("GEMINI 2.5 COMPUTER USE - AGENTIC WEB AUTOMATION (ANY WEBSITE)")
    logger.info("="*150 + "\n")
    logger.info(f"[CONFIG] Computer Use Model: {settings.computer_use_model}")
    
    # FIXED: Changed headless_mode to headless, and viewport attributes
    logger.info(f"[CONFIG] API Key: {settings.gemini_api_key[:30]}...")
    logger.info(f"[CONFIG] Browser: {settings.browser_type}")
    logger.info(f"[CONFIG] Headless: {settings.headless}")
    logger.info(f"[CONFIG] Anti-Bot: {settings.anti_bot_enabled}\n")


def display_main_menu():
    """Display main menu"""
    
    print("\n" + "="*150)
    print("MAIN MENU - REAL WEBSITE AUTOMATION")
    print("="*150)
    print("\n1. Run DemoQA Test (Learning)")
    print("2. Automate Amazon (Search Product)")
    print("3. Automate YouTube (Search Videos)")
    print("4. Automate Yahoo Finance (Search Stock Prices)")
    print("5. Automate MakeMyTrip (Search Flights)")
    print("6. Automate Custom Website (User Prompt)")
    print("7. View Supported Websites")
    print("8. View Settings")
    print("9. Exit")
    print("\n" + "="*150)


def run_demoqa_task():
    """Run DemoQA test task - automatic, no user prompt needed"""
    
    automation_engine = None
    
    try:
        logger.info("[TASK] DemoQA Intelligence Extraction (Automatic)\n")
        
        logger.info("[BROWSER] Initializing...")
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        task_prompt = """
        Explore DemoQA modules using DIRECT URLs (do NOT go back to homepage between sections):
        
        1. You are already on https://demoqa.com/ — take a screenshot of the homepage
        2. Navigate to https://demoqa.com/elements — click "Text Box" in the sidebar, fill the form with sample data, click Submit, screenshot the output
        3. Navigate to https://demoqa.com/forms — click "Practice Form", fill a few fields (name, email, gender), screenshot
        4. Navigate to https://demoqa.com/alertsWindows — click "Alerts", trigger alert buttons, screenshot
        5. Navigate to https://demoqa.com/widgets — click "Accordian", expand sections, screenshot
        6. Navigate to https://demoqa.com/interaction — click "Droppable", try drag and drop, screenshot
        7. Navigate to https://demoqa.com/books — screenshot the book store listing
        
        For each section: interact with at least one sub-item, take screenshots, and document what you find.
        Generate a complete intelligence report at the end.
        """
        
        results = automation_engine.execute_agentic_task(
            task_prompt,
            target_url="https://demoqa.com/"
        )
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def run_amazon_task():
    """Run Amazon task with user-provided prompt"""
    
    automation_engine = None
    
    try:
        print("\n" + "="*150)
        print("AMAZON AUTOMATION - AI Agent")
        print("="*150)
        print("\nTell the AI agent what to do on Amazon:")
        print("\nEXAMPLE PROMPTS:")
        print('  "Search for iPhone 16 Pro Max and show me the top 3 results with prices"')
        print('  "Find wireless earbuds under $50 with 4+ star rating"')
        print('  "Search for gaming laptop and compare the first 3 options"')
        print('  "Look up Samsung Galaxy S25 Ultra and get the price, colors, and reviews"')
        print("="*150)
        
        task_prompt = input("\nYour task for Amazon: ").strip()
        
        if not task_prompt:
            logger.warning("[TASK] Empty task - cancelled")
            return
        
        logger.info(f"[TASK] Amazon: {task_prompt}\n")
        logger.info("[BROWSER] Initializing...")
        
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        results = automation_engine.execute_agentic_task(
            task_prompt,
            target_url="https://www.amazon.com",
            website_type="amazon"
        )
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def run_youtube_task():
    """Run YouTube task with user-provided prompt"""
    
    automation_engine = None
    
    try:
        print("\n" + "="*150)
        print("YOUTUBE AUTOMATION - AI Agent")
        print("="*150)
        print("\nTell the AI agent what to do on YouTube:")
        print("\nEXAMPLE PROMPTS:")
        print('  "Search for A.R. Rahman songs and play the first video"')
        print('  "Find the latest Python tutorial videos and show the top 5 results"')
        print('  "Search for cooking recipes for biryani and get view counts"')
        print('  "Look up Tesla Cybertruck review and get the video details"')
        print("="*150)
        
        task_prompt = input("\nYour task for YouTube: ").strip()
        
        if not task_prompt:
            logger.warning("[TASK] Empty task - cancelled")
            return
        
        logger.info(f"[TASK] YouTube: {task_prompt}\n")
        logger.info("[BROWSER] Initializing...")
        
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        results = automation_engine.execute_agentic_task(
            task_prompt,
            target_url="https://www.youtube.com",
            website_type="youtube"
        )
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def run_yahoo_finance_task():
    """Run Yahoo Finance task with user-provided prompt"""
    
    automation_engine = None
    
    try:
        print("\n" + "="*150)
        print("YAHOO FINANCE AUTOMATION - AI Agent")
        print("="*150)
        print("\nTell the AI agent what to do on Yahoo Finance:")
        print("\nEXAMPLE PROMPTS:")
        print('  "Get the current stock price of Tesla (TSLA) with key metrics"')
        print('  "Search for Apple stock and show me the 52-week high and low"')
        print('  "Look up NVIDIA (NVDA) and get market cap, P/E ratio, and volume"')
        print('  "Compare the stock prices of Google and Microsoft"')
        print("="*150)
        
        task_prompt = input("\nYour task for Yahoo Finance: ").strip()
        
        if not task_prompt:
            logger.warning("[TASK] Empty task - cancelled")
            return
        
        logger.info(f"[TASK] Yahoo Finance: {task_prompt}\n")
        logger.info("[BROWSER] Initializing...")
        
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        results = automation_engine.execute_agentic_task(
            task_prompt,
            target_url="https://finance.yahoo.com",
            website_type="yahoo_finance"
        )
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def run_makemytrip_task():
    """Run MakeMyTrip task with user-provided prompt"""
    
    automation_engine = None
    
    try:
        print("\n" + "="*150)
        print("MAKEMYTRIP AUTOMATION - AI Agent")
        print("="*150)
        print("\nTell the AI agent what to do on MakeMyTrip:")
        print("\nEXAMPLE PROMPTS:")
        print('  "Search for one-way flights from Delhi to Mumbai for tomorrow"')
        print('  "Find cheapest round-trip flights from Bangalore to Goa next week"')
        print('  "Search for hotels in Jaipur for 2 adults, show top 3 with prices"')
        print('  "Look up flight options from Chennai to Hyderabad and compare airlines"')
        print("="*150)
        
        task_prompt = input("\nYour task for MakeMyTrip: ").strip()
        
        if not task_prompt:
            logger.warning("[TASK] Empty task - cancelled")
            return
        
        logger.info(f"[TASK] MakeMyTrip: {task_prompt}\n")
        logger.info("[BROWSER] Initializing...")
        
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        results = automation_engine.execute_agentic_task(
            task_prompt,
            target_url="https://www.makemytrip.com",
            website_type="makemytrip"
        )
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def run_custom_website_task():
    """Run task on ANY website - user provides the full instruction"""
    
    automation_engine = None
    
    try:
        print("\n" + "="*150)
        print("CUSTOM WEBSITE AUTOMATION - AI Agent")
        print("="*150)
        print("\nTell the AI agent what to do on any website:")
        print("\nEXAMPLE PROMPTS:")
        print('  "Go to github.com and search for Python machine learning repositories"')
        print('  "Go to booking.com and find hotels in Paris for next weekend"')
        print('  "Go to flipkart.com and search for laptops under 50000 rupees"')
        print('  "Go to wikipedia.org and search for artificial intelligence"')
        print("="*150)
        
        task_prompt = input("\nYour task: ").strip()
        
        if not task_prompt:
            logger.warning("[TASK] Empty task - cancelled")
            return
        
        if len(task_prompt) < 10:
            logger.warning("[TASK] Task too short (minimum 10 characters)")
            return
        
        logger.info(f"[TASK] Custom: {task_prompt}\n")
        logger.info("[BROWSER] Initializing...")
        
        automation_engine = AutomationEngine()
        
        if not automation_engine.initialize_driver("chrome"):
            logger.error("[BROWSER] Failed")
            return
        
        logger.info("[BROWSER] Ready\n")
        
        logger.info("[EXECUTION] Starting Gemini 2.5 Computer Use with intelligent fallback...\n")
        
        results = automation_engine.execute_agentic_task(task_prompt)
        
        _display_results(results)
        
        logger.info("\n[INSPECTION] Browser remains open for 3 seconds...")
        time.sleep(3)
    
    except KeyboardInterrupt:
        logger.info("[INTERRUPT] Task interrupted by user")
    
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if automation_engine:
            logger.info("[BROWSER] Closing...")
            automation_engine.close_driver()


def view_supported_websites():
    """Display supported websites with descriptions"""
    
    logger.info("\n" + "="*150)
    logger.info("SUPPORTED WEBSITES & WORKFLOWS")
    logger.info("="*150)
    
    websites = {
        'amazon.com': 'Product search, pricing, reviews, variants, add to cart',
        'youtube.com': 'Video search, channel exploration, playlist browsing, view metrics',
        'makemytrip.com': 'Flight search, hotel booking, travel packages, price comparison',
        'finance.yahoo.com': 'Stock quotes, market data, price trends, company metrics',
        'github.com': 'Repository search, code exploration, trending projects, user profiles',
        'booking.com': 'Hotel search, flight booking, property details, reviews',
        'flipkart.com': 'Product search, Indian e-commerce, price comparison, deals',
        'alibaba.com': 'Bulk product search, wholesale pricing, supplier details',
        'google.com': 'General search, information retrieval, link extraction',
        'wikipedia.org': 'Information lookup, article navigation, content extraction',
        'demoqa.com': 'Test automation learning platform with various UI elements',
        'Any other website': 'Custom URL automation with generic selectors'
    }
    
    for website, description in websites.items():
        logger.info(f"  {website:<25} - {description}")
    
    logger.info("\n" + "="*150 + "\n")


def view_settings():
    """Display current settings"""
    
    logger.info("\n" + "="*150)
    logger.info("CURRENT SETTINGS")
    logger.info("="*150)
    
    logger.info("\n[API]")
    logger.info(f"  Model: {settings.gemini_model}")
    logger.info(f"  API Key: {settings.gemini_api_key[:40]}...")
    
    logger.info("\n[BROWSER]")
    logger.info(f"  Type: {settings.browser_type}")
    logger.info(f"  Headless: {settings.headless}")
    logger.info(f"  Viewport: {settings.viewport_width}x{settings.viewport_height}")
    
    logger.info("\n[TIMEOUTS]")
    logger.info(f"  Page Load: {settings.page_load_timeout}s")
    logger.info(f"  Element Wait: {settings.element_wait_timeout}s")
    
    logger.info("\n[ANTI-BOT]")
    logger.info(f"  Enabled: {settings.anti_bot_enabled}")
    logger.info(f"  Stealth: {settings.enable_stealth}")
    logger.info(f"  Random Delay: {settings.random_delay}")
    
    logger.info("\n[DATABASE]")
    logger.info(f"  URL: {settings.database_url}")
    
    logger.info("\n" + "="*150 + "\n")


def _display_results(results: dict):
    """Display execution results"""
    
    logger.info("\n" + "="*150)
    logger.info("EXECUTION RESULTS")
    logger.info("="*150)
    
    logger.info(f"Status: {results.get('status', 'Unknown')}")
    logger.info(f"Task ID: {results.get('task_id', 'N/A')}")
    
    if results.get('error'):
        logger.error(f"Error: {results['error']}")
    else:
        logger.info(f"Navigation URL: {results.get('navigation_url', 'N/A')}")
        logger.info(f"Actual URL: {results.get('actual_url', 'N/A')}")
        logger.info(f"Total Iterations: {results.get('total_iterations', 0)}")
        logger.info(f"Total Actions: {results.get('total_actions', 0)}")
        logger.info(f"Pages Visited: {len(results.get('unique_pages', []))}")
        logger.info(f"Execution Time: {results.get('execution_time', 0):.1f}s")
        logger.info(f"Gemini Used: {results.get('gemini_used', False)}")
        logger.info(f"Fallback Used: {results.get('fallback_used', False)}")
        
        # Display AI Summary (model's analysis/report)
        if results.get('ai_summary'):
            logger.info("\n" + "-"*150)
            logger.info("AI AGENT SUMMARY")
            logger.info("-"*150)
            summary = results['ai_summary']
            # Print each line of the summary
            for line in summary.split('\n'):
                if line.strip():
                    logger.info(f"  {line.strip()}")
            logger.info("-"*150)
        
        # Display extracted data if available
        if results.get('extracted_data'):
            logger.info(f"\n[EXTRACTED DATA]")
            logger.info(json.dumps(results['extracted_data'], indent=2))
    
    logger.info("="*150 + "\n")


def main():
    """Main application loop"""
    
    try:
        initialize_application()
        
        while True:
            try:
                display_main_menu()
                
                choice = input("\nEnter choice (1-9): ").strip()
                
                if choice == "1":
                    run_demoqa_task()
                
                elif choice == "2":
                    run_amazon_task()
                
                elif choice == "3":
                    run_youtube_task()
                
                elif choice == "4":
                    run_yahoo_finance_task()
                
                elif choice == "5":
                    run_makemytrip_task()
                
                elif choice == "6":
                    run_custom_website_task()
                
                elif choice == "7":
                    view_supported_websites()
                
                elif choice == "8":
                    view_settings()
                
                elif choice == "9":
                    logger.info("[EXIT] Goodbye!")
                    break
                
                else:
                    logger.warning("[INPUT] Invalid choice. Please enter 1-9.")
                
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                logger.info("[INTERRUPT] Keyboard interrupt detected")
                break
            
            except Exception as e:
                logger.error(f"[ERROR] Menu error: {str(e)}")
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()