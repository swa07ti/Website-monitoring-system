import time
import requests
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_client import make_asgi_app, Gauge, Counter
import uvicorn

app = FastAPI(title="Advanced SRE Monitor")

# ==========================================
# PROMETHEUS METRICS (HIGH-LEVEL)
# ==========================================
WEBSITE_UP = Gauge('website_up', 'Uptime status (1=UP, 0=DOWN)', ['url'])
RESPONSE_TIME = Gauge('website_response_time_ms', 'Response time in ms', ['url'])
HTTP_STATUS = Gauge('website_http_status_code', 'HTTP Status Code', ['url'])
TOTAL_CHECKS = Counter('website_checks_total', 'Total number of checks performed', ['url'])
FAILED_CHECKS = Counter('website_checks_failed_total', 'Total number of failed checks', ['url'])

# In-memory database of monitored URLs
MONITORED_URLS = {
    "https://www.google.com",
    "https://www.github.com",
    "https://this-site-probably-does-not-exist.com"
}

# Mount Prometheus metrics endpoint so Prometheus can scrape it
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Setup HTML templates for the Control Center UI
templates = Jinja2Templates(directory="templates")

# ==========================================
# FASTAPI ROUTES (USER INTERFACE)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the SRE Control Center Dashboard"""
    return templates.TemplateResponse(request=request, name="index.html", context={"urls": list(MONITORED_URLS)})

@app.post("/add")
async def add_url(request: Request, url: str = Form(...)):
    """Dynamically add a new website to monitor"""
    if not url.startswith("http"):
        url = "https://" + url
    MONITORED_URLS.add(url)
    return templates.TemplateResponse(request=request, name="index.html", context={"urls": list(MONITORED_URLS)})

@app.post("/remove")
async def remove_url(request: Request, url: str = Form(...)):
    """Dynamically stop monitoring a website"""
    if url in MONITORED_URLS:
        MONITORED_URLS.remove(url)
    return templates.TemplateResponse(request=request, name="index.html", context={"urls": list(MONITORED_URLS)})

# ==========================================
# MONITORING ENGINE (BACKGROUND TASK)
# ==========================================
async def check_website(url):
    """Async wrapper to check website status without blocking the API"""
    try:
        start_time = time.time()
        # Run synchronous requests in a threadpool so we don't block the FastAPI web server
        response = await asyncio.to_thread(requests.get, url, timeout=5)
        end_time = time.time()
        
        response_time_ms = round((end_time - start_time) * 1000, 2)
        HTTP_STATUS.labels(url=url).set(response.status_code)
        TOTAL_CHECKS.labels(url=url).inc()
        
        if response.status_code < 400:
            WEBSITE_UP.labels(url=url).set(1)
            RESPONSE_TIME.labels(url=url).set(response_time_ms)
            print(f"[UP] {url} ({response.status_code}) - {response_time_ms}ms")
        else:
            WEBSITE_UP.labels(url=url).set(0)
            RESPONSE_TIME.labels(url=url).set(0)
            FAILED_CHECKS.labels(url=url).inc()
            print(f"[DOWN] {url} - Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        WEBSITE_UP.labels(url=url).set(0)
        RESPONSE_TIME.labels(url=url).set(0)
        HTTP_STATUS.labels(url=url).set(0)
        TOTAL_CHECKS.labels(url=url).inc()
        FAILED_CHECKS.labels(url=url).inc()
        print(f"[DOWN] {url} - Connection Error")

async def monitoring_loop():
    """Background task to continually monitor all registered URLs"""
    while True:
        # Create a copy to avoid 'Set changed size during iteration' errors
        urls_to_check = list(MONITORED_URLS)
        for url in urls_to_check:
            asyncio.create_task(check_website(url))
        
        # Check every 10 seconds
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Start the background monitoring engine when the web server starts"""
    print("Starting SRE Monitoring Engine...")
    asyncio.create_task(monitoring_loop())

if __name__ == '__main__':
    # Start the robust Uvicorn ASGI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
