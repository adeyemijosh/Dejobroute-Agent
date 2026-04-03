"""
TechJobs Backend — FastAPI + Desearch API
Handles Desearch streaming SSE response correctly.
"""

import os
import re
import json
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI(title="TechJobs API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DESEARCH_API_KEY  = os.getenv("DESEARCH_API_KEY", "")
DESEARCH_BASE_URL = "https://api.desearch.ai"

CATEGORY_PROMPTS = {
    "all":         "tech jobs hiring now software engineer developer designer product manager data scientist devops marketing",
    "engineering": "software engineer developer backend frontend fullstack mobile hiring job opening now",
    "marketing":   "marketing manager digital marketing SEO content strategist social media manager hiring now",
    "design":      "UX designer UI designer product designer graphic designer hiring job opening now",
    "product":     "product manager product owner APM senior PM hiring job opening now",
    "data":        "data scientist data analyst data engineer ML engineer machine learning hiring now",
    "devops":      "devops engineer cloud engineer SRE site reliability kubernetes infrastructure hiring now",
    "sales":       "sales account executive business development SDR BDR sales manager hiring now",
}

DATE_FILTER_MAP = {
    "24h": "PAST_24_HOURS",
    "7d":  "PAST_WEEK",
    "30d": "PAST_MONTH",
}


def parse_streaming_response(raw_text: str) -> str:
    completion_text = ""
    text_chunks = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        json_str = line[5:].strip()
        if not json_str:
            continue
        try:
            obj = json.loads(json_str)
        except Exception:
            continue

        if obj.get("type") == "completion":
            completion_text = obj.get("content", "")
        elif obj.get("type") == "text":
            text_chunks.append(obj.get("content", ""))

    return completion_text or "".join(text_chunks)


def build_job_cards(completion_text: str) -> list:
    jobs = []

    pattern = r'([^.!?\n]{20,500}?)\s*\[source\]\((https://x\.com/[^\)]+)\)'
    matches = re.findall(pattern, completion_text, re.DOTALL)

    for i, (snippet, url) in enumerate(matches):
        snippet = snippet.strip().replace('\n', ' ')
        url_match = re.match(r'https://x\.com/([^/]+)/status/(\d+)', url)
        username = url_match.group(1) if url_match else "unknown"
        tweet_id = url_match.group(2) if url_match else str(i)

        role    = extract_role(snippet)
        company = extract_company(snippet, username)

        jobs.append({
            "id":       tweet_id,
            "role":     role,
            "company":  company,
            "username": username,
            "text":     snippet,
            "url":      url,
            "posted":   "Recent",
        })

    if not jobs:
        urls = re.findall(r'https://x\.com/[^\s\)\"\']+/status/\d+', completion_text)
        seen_urls = set()
        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            url_match = re.match(r'https://x\.com/([^/]+)/status/(\d+)', url)
            username = url_match.group(1) if url_match else "unknown"
            tweet_id = url_match.group(2) if url_match else url
            jobs.append({
                "id":       tweet_id,
                "role":     "Tech Role",
                "company":  username,
                "username": username,
                "text":     "View the original post for full details.",
                "url":      url,
                "posted":   "Recent",
            })

    return jobs


def extract_role(text: str) -> str:
    patterns = [
        r'hiring (?:a |an )?([A-Z][a-zA-Z\s/\-]+?)(?:\s+with|\s+specializing|\s+in\s+[A-Z]|\s+remotely|,|\.|$)',
        r'seeking (?:a |an )?([A-Z][a-zA-Z\s/\-]+?)(?:\s+with|\s+specializing|,|\.|$)',
        r'recruiting ([A-Z][a-zA-Z\s/\-]+?)(?:\s+with|\s+focusing|,|\.|$)',
        r'for (?:a |an )?([A-Z][a-zA-Z\s/\-]{4,50}?) (?:role|position|opening)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            candidate = m.group(1).strip().rstrip(".,!-– ")
            if 3 < len(candidate) < 70:
                return candidate
    return "Tech Role"


def extract_company(text: str, username: str) -> str:
    m = re.match(r'^([A-Z][a-zA-Z0-9\s&]+?)\s+(?:is|are)\s+(?:also\s+)?(?:hiring|seeking|recruiting)', text)
    if m:
        candidate = m.group(1).strip()
        if 2 < len(candidate) < 60:
            return candidate
    return username


@app.get("/")
def root():
    return {"status": "TechJobs API running"}


@app.get("/api/jobs")
async def search_jobs(
    category:    str           = Query("all"),
    date_filter: str           = Query("7d"),
    query:       Optional[str] = Query(None),
    count:       int           = Query(20, ge=10, le=100),
):
    if not DESEARCH_API_KEY:
        return JSONResponse(
            status_code=500,
            content={"error": "DESEARCH_API_KEY not set in .env"},
        )

    base_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["all"])
    if query:
        base_prompt = f"{query} {base_prompt}"

    payload = {
        "prompt":      base_prompt,
        "tools":       ["twitter"],
        "result_type": "LINKS_WITH_FINAL_SUMMARY",
        "count":       count,
        "date_filter": DATE_FILTER_MAP.get(date_filter, "PAST_WEEK"),
        "streaming":   True,
    }

    headers = {
        "Authorization": DESEARCH_API_KEY,
        "Content-Type":  "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{DESEARCH_BASE_URL}/desearch/ai/search",
                json=payload,
                headers=headers,
            )
        except httpx.ConnectError as e:
            return JSONResponse(
                status_code=503,
                content={"error": f"Cannot connect to Desearch: {str(e)}"},
            )

    if resp.status_code != 200:
        return JSONResponse(
            status_code=resp.status_code,
            content={"error": f"Desearch error {resp.status_code}: {resp.text[:300]}"},
        )

    completion = parse_streaming_response(resp.text)

    if not completion:
        return JSONResponse(
            status_code=502,
            content={"error": "Desearch returned empty response. Try again."},
        )

    jobs = build_job_cards(completion)

    seen, unique = set(), []
    for job in jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)

    return {
        "total":       len(unique),
        "category":    category,
        "date_filter": date_filter,
        "jobs":        unique,
    }


@app.get("/api/categories")
def get_categories():
    return {"categories": list(CATEGORY_PROMPTS.keys())}