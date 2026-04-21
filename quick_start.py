"""
QUICK START - Web Automation Framework
Copy this to your project and run it directly
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main automation entry point"""
    
    print("\n" + "="*100)
    print("WEB AUTOMATION FRAMEWORK - QUICK START")
    print("="*100 + "\n")
    
    try:
        # Import with error handling
        try:
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
        except ImportError:
            print("❌ Missing dependencies!")
            print("Run: pip install selenium webdriver-manager beautifulsoup4 groq")
            return
        
        try:
            from project.computer_use_loop import ComputerUseLoop
        except ImportError:
            print("❌ Cannot find project modules!")
            print("Make sure files are in project/ directory")
            return
        
        print("✓ All dependencies loaded\n")
        
        # Setup Chrome driver
        print("[SETUP] Initializing browser...")
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✓ Browser ready\n")
        except Exception as error:
            print(f"❌ Browser error: {error}")
            return
        
        try:
            # Initialize automation loop
            print("[INIT] Loading automation engine...")
            loop = ComputerUseLoop(driver)
            print("✓ Automation engine ready\n")
            
            # Define task
            task_prompt = "Search for python tutorials on youtube and click the first video"
            target_url = "https://www.youtube.com"
            
            print(f"[TASK] {task_prompt}")
            print(f"[URL] {target_url}\n")
            
            # Execute automation
            print("[EXECUTE] Starting automation...\n")
            results = loop.execute_automation(
                task_prompt=task_prompt,
                target_url=target_url,
                max_iterations=20
            )
            
            # Print results
            print("\n" + "="*100)
            print("EXECUTION COMPLETE")
            print("="*100)
            print(f"Status: {results['status']}")
            print(f"Workflow: {results['workflow_type']}")
            print(f"Iterations: {results['total_iterations']}")
            print(f"Actions: {results['total_actions']}")
            print(f"Time: {results['execution_time']:.1f}s")
            print(f"Groq Used: {results['groq_used']}")
            print("="*100 + "\n")
            
        finally:
            print("[CLEANUP] Closing browser...")
            driver.quit()
            print("✓ Done\n")
    
    except Exception as error:
        print(f"\n❌ ERROR: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()