from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import subprocess

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    # Correct relative path inside Docker (/app/static/index.html)
    return FileResponse("frontend/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    mode: str = Field(
        ...,
        description="Operation mode: 'IBAN' or 'KNRBLZ'",
        example="IBAN",
    )
    value1: str = Field(
        ...,
        description="IBAN or KNR depending on mode",
        example="DE02120300000000202051",
    )
    value2: str | None = Field(
        None,
        description="BLZ value (required only for KNRBLZ mode)",
        example="12030000",
    )


@app.post("/run")
def run(req: Request):
    mode = req.mode.upper()

    if mode == "IBAN":
        input_text = f"IBAN\n{req.value1}\n"

    elif mode == "KNRBLZ":
        if req.value2 is None:
            raise HTTPException(
                status_code=400,
                detail="value2 (BLZ) required for KNRBLZ mode"
            )
        input_text = f"KNRBLZ\n{req.value1}\n{req.value2}\n"

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
    for i in lines:
        if "=" in i:
            k , v = i.split("=",1)
            if ((k == "BLZ" or k == "KNR") and mode == "IBAN") or (k == "IBAN" and mode == "KNRBLZ"):
                resultnew[k] = v           
    return resultnew