from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict

app = FastAPI()


class AdvancedMiddleWare (BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_limit_records: Dict[str, float] = defaultdict(float)

    async def log_messages(self, messages: str):
        print(messages)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if current_time - self.request_limit_records[client_ip] < 1:
            return Response("Too many requests", status_code=429)

        # Update the last request time for the client
        self.request_limit_records[client_ip] = current_time
        path = request.url.path
        await self.log_messages(f"Request from {client_ip} to {path}")

        # Process the request and measure the time taken
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time

        # Add a custom header with the processing time
        custom_header = {"X-Processing-Time": str(processing_time)}
        for header, value in custom_header.items():
            response.headers.append(header, value)
        
        # Log the response details
        await self.log_messages(f"Response sent to {client_ip} for {path} in {processing_time:.2f} seconds")

        return response
        
app.add_middleware(AdvancedMiddleWare)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}