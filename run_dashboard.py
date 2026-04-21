"""
Dashboard API Server Entry Point
Run: python run_dashboard.py
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  GEMINI WEB AUTOMATION — DASHBOARD API SERVER")
    print("=" * 80)
    print("  API Docs:    http://localhost:8000/docs")
    print("  Frontend:    http://localhost:5173  (run 'npm run dev' in frontend/)")
    print("=" * 80 + "\n")

    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["api"],
    )
