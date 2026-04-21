# Enterprise Web Automation Framework

A production-grade, agentic web automation framework powered by **Gemini 2.5 Computer Use Model**. It features intelligent fallback analysis, natural language task execution, advanced anti-bot detection bypass, industrial standards, and an enterprise-level architecture.

## 🌟 Key Features

- **🤖 LLM-Powered Agent (Gemini 2.5 Computer Use Model)**: Execute complex web automation tasks simply by providing a natural language prompt. Read more about the model: [Gemini Computer Use Model](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-computer-use-model/)
- **🌐 Universal Website Support**: Out-of-the-box workflows for Amazon, YouTube, MakeMyTrip, Yahoo Finance, GitHub, Booking, Flipkart, Alibaba, plus a generic fallback engine to handle **any** custom website dynamically.
- **🛡️ Anti-Bot & Stealth Mode**: Advanced bypass techniques including user-agent rotation, header randomization, realistic human typing, and random action delays to evade bot detection.
- **🔄 Intelligent Fallback**: Dynamically switches to intelligent DOM-based UI analysis and interaction when standard workflow steps fail or encounter unexpected site changes.
- **⚙️ Enterprise Architecture**: Built with robust configuration management (Pydantic), structured logging (Structlog), database persistence (SQLAlchemy), and retry logic with exponential backoff.
- **💻 Multi-Browser Support**: Integrated with Playwright and Selenium (`undetected-chromedriver`) for maximum flexibility and stealth.

![alt text](image.png)

## 🛠️ Technologies Used

### Backend
- **AI/LLM Engine**: Google Generative AI (`google-generativeai`)
- **Browser Automation**: Playwright, Selenium (`undetected-chromedriver`)
- **API Framework**: FastAPI with WebSockets for real-time updates
- **Configuration**: Pydantic v2, `python-dotenv`
- **Database / Persistence**: SQLAlchemy
- **Language**: Python 3.8+
- **Logging**: structlog, python-json-logger

### Frontend
- **Framework**: React 19 (Vite, TypeScript)
- **Routing**: React Router 7
- **Data Visualization**: Recharts
- **Icons**: Lucide React
- **Date Utilities**: date-fns

## 🚀 Installation & Setup

### Backend Setup
1. **Create Virtual Environment**: Create a Python virtual environment and activate it.
2. **Install Dependencies**: Install the required packages from `requirements.txt`.
3. **Configure Environment**: Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
4. **Run the Framework**: Start the application from `main.py`.

### Frontend Setup
1. **Navigate to Frontend**: Enter the `frontend` directory.
2. **Install Dependencies**: Install the required node packages using `npm install`.
3. **Run the Dashboard**: Start the development server using `npm run dev`.

## 🎮 Usage

Upon starting the application through `main.py`, you will be presented with a robust, interactive terminal interface:

```text
======================================================================================================================================================
MAIN MENU - REAL WEBSITE AUTOMATION
======================================================================================================================================================

1. Run DemoQA Test (Learning)
2. Automate Amazon (Search Product)
3. Automate YouTube (Search Videos)
4. Automate Yahoo Finance (Search Stock Prices)
5. Automate MakeMyTrip (Search Flights)
6. Automate Custom Website (User Prompt)
7. View Supported Websites
8. View Settings
9. Exit
```

You can select a pre-defined workflow tailored for specific sites (options 1-5), or select **Option 6** to execute zero-shot custom tasks via natural language, for example:
> *"Go to amazon.com and find iPhone 15 Pro Max price and variants"*

## 🏗️ Project Structure & Context

- `agents/`: Gemini-based task logic, prompt analysis, and agentic computer use integrations.
- `api/`: FastAPI server implementation handling REST endpoints and WebSocket log streaming.
- `chrome/`: Chrome profile management and driver optimization settings.
- `config/`: Centralized Pydantic configuration module parsing the `.env` settings.
- `core/`: The core `AutomationEngine` tying together browser operations and ML agent logic.
- `detectors/`: Modules for detecting page elements and bot-protection mechanisms.
- `frontend/`: React-based dashboard for real-time monitoring and control.
- `handlers/`: Specific interaction handlers for various website components.
- `logging_config/`: Robust JSON/Structlog configuration for enterprise-grade tracing.
- `persistence/`: SQLite/Database storage bindings via SQLAlchemy for task history.
- `selenium_driver/`: Browser instantiation and stealth setups for undetected automation.
- `utils/`: Common utilities for file handling, image processing, and string manipulation.
- `workflows/`: Pre-defined automation routines for target websites (Amazon, YouTube, etc.).
