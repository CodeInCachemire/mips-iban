from contextlib import asynccontextmanager
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend import db


import subprocess


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield
app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/history")
def read_history():
    rows = db.read_conversion()
    data = []
    for row in rows:
        entry = {
            "id" : row[0],
            "direction" : row[1],
            "input" : json.loads(row[2]),
            "output" : json.loads(row[3]),
            "created_at": row[4],
        }
        data.append(entry)
    return data

def mask_number(s:str, mask_char="*"):
    return s[:2] + mask_char * (len(s) - 5) + s[-3:]
def mask_iban(s:str, mask_char="*"):
    return s[:6] + mask_char * (len(s) - 9) + s[-3:]

@app.get("/")
def serve_frontend():
    # Correct relative path inside Docker (/app/static/index.html)
    return FileResponse("frontend/index.html")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

class Request(BaseModel):
    mode: str = Field(
        ...,
        description="Operation mode: 'IBAN' or 'KNRBLZ'",
        json_schema_extra={"example": "IBAN"},
    )
    value1: str = Field(
        ...,
        description="IBAN or KNR depending on mode",
        json_schema_extra={"example": "DE02120300000000202051"},
    )
    value2: str | None = Field(
        None,
        description="BLZ value (required only for KNRBLZ mode)",
        json_schema_extra={"example": "12030000"},
    )


@app.post("/run")
def run(req: Request):
    mode = req.mode.upper()
    input_dict = {}

    if mode == "IBAN":
        input_text = f"IBAN\n{req.value1.upper()}\n"
        masked_input = mask_iban(req.value1.upper())
        input_dict = {"IBAN":masked_input}

    elif mode == "KNRBLZ":
        if req.value2 is None:
            raise HTTPException(
                status_code=400,
                detail="value2 (BLZ) required for KNRBLZ mode"
            )
        input_text = f"KNRBLZ\n{req.value1}\n{req.value2}\n"
        masked_KNR = mask_number(req.value1)
        masked_BLZ = mask_number(req.value2)
        input_dict = {"KNR":masked_KNR, "BLZ" :masked_BLZ}

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Use 'IBAN' or 'KNRBLZ'."
        )

    cmd = [
        "java", "-jar", "/app/mars.jar",
        "ae127",          # assembler error exit code
        "se126",          # simulator error exit code
        "me",             # terminate on runtime error
        "nc",             # no copyright
        "sm", "50000000", # max instruction steps
        "/app/src/iban2knr.asm",
        "/app/src/knr2iban.asm",
        "/app/src/moduloStr.asm",
        "/app/src/verify_iban.asm",
        "/app/src/util.asm",
        "/app/src/validateChecksum.asm",
        "/app/src/main.asm",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=input_text,     
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="MIPS execution timed out"
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=e.stderr or "MIPS execution failed"
        )
    
    lines = result.stdout.splitlines()

    if not lines:
        raise HTTPException(
            status_code=500,
            detail="No output from MIPS program execution"
        )

    if lines[0] == "ERR":
        message = "Unknown error"
        for line in lines:
            if line.startswith("MSG="):
                message = line.split("=", 1)[1]
        raise HTTPException(status_code=400, detail=message)

    resultnew = {}
    output_masked = {}
    for i in lines:
        if i.startswith("MSG="):
            status_msg = i.split("=", 1)[1]
        elif "=" in i:
            k , v = i.split("=",1)
            if ((k == "BLZ" or k == "KNR") and mode == "IBAN") or (k == "IBAN" and mode == "KNRBLZ"):
                resultnew[k] = v
                output_masked[k] = mask_number(v)
    if mode =="KNRBLZ":
        status_msg = "Successful KNR and BLZ parsed and valid IBAN generated!"
    response_new = {"status_msg" : status_msg, "result" : resultnew}
    db.log_conversion(mode, json.dumps(input_dict), json.dumps(output_masked))  
    return response_new

