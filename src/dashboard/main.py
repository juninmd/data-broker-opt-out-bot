import csv
import io
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from src.db.database import (
    init_db,
    get_requests,
    get_broker_health,
    verify_and_use_otp_token,
    create_session,
)
from src.dashboard.auth import require_auth, COOKIE_NAME

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Data Broker Opt-Out Dashboard", lifespan=lifespan)

@app.get("/auth/login")
async def login(token: str, request: Request):
    if verify_and_use_otp_token(token):
        session_id = create_session()
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key=COOKIE_NAME,
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=86400, # 24 hours
        )
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP token."
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, authenticated: bool = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/dashboard/timeline", response_class=HTMLResponse)
async def timeline_component(request: Request, authenticated: bool = Depends(require_auth)):
    requests_data = get_requests()
    return templates.TemplateResponse(request=request, name="timeline.html", context={"requests": requests_data})

@app.get("/dashboard/broker-health", response_class=HTMLResponse)
async def broker_health_component(request: Request, authenticated: bool = Depends(require_auth)):
    health_data = get_broker_health()
    return templates.TemplateResponse(request=request, name="broker_health.html", context={"health_records": health_data})

@app.get("/dashboard/export")
async def export_data(authenticated: bool = Depends(require_auth)):
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Requests section
    writer.writerow(["=== REQUEST TIMELINE ==="])
    writer.writerow(["ID", "Broker Name", "Request Type", "Status", "Details", "Created At", "Updated At"])
    for req in get_requests():
        writer.writerow([
            req["id"],
            req["broker_name"],
            req["request_type"],
            req["status"],
            req["details"],
            req["created_at"],
            req["updated_at"]
        ])

    writer.writerow([])
    # Write Health section
    writer.writerow(["=== BROKER HEALTH ==="])
    writer.writerow(["Broker Name", "Status", "Response Time (ms)", "Last Check"])
    for bh in get_broker_health():
        writer.writerow([
            bh["broker_name"],
            bh["status"],
            bh["response_time_ms"],
            bh["last_check"]
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=opt_out_dashboard_export.csv"}
    )
