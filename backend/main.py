from fastapi import FastAPI,  HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

import subprocess

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="../frontend"),
    name="static"
)

@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")
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
        description=(
            "For IBAN mode: full IBAN string\n"
            "For KNRBLZ mode: KNR value"
        ),
        example="DE02120300000000202051",
    )
    value2: str | None = Field(
        None,
        description="BLZ value (required only for KNRBLZ mode)",
        example="12030000",
    )


@app.post(
    "/run",
    summary="Convert IBAN ↔ KNR+BLZ",
    description=(
        "Supports two modes:\n\n"
        "- **IBAN** → returns BLZ and KNR\n"
        "- **KNRBLZ** → returns IBAN\n\n"
        "The backend runs a MIPS program inside Docker."
    ),
)
def run(req: Request):
    mode=req.mode.upper()
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
    
    result = subprocess.run(
        ["docker", "run", "-i", "iban-mips"],
        input=input_text,
        text=True,
        capture_output=True
    )

    #in case of docker errors or failed execution
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail="Docker execution failed"
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

        raise HTTPException(
            status_code=400,
            detail=message
        )
    
    resultnew = {}
    for i in lines:
        if "=" in i:
            k , v = i.split("=",1)
            if ((k == "BLZ" or k == "KNR") and mode == "IBAN") or (k == "IBAN" and mode == "KNRBLZ"):
                resultnew[k] = v           
    return resultnew
