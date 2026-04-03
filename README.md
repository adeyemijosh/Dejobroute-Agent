# TechJobs — Live Job Discovery from Twitter

A real-time tech job discovery platform that pulls live job postings directly from Twitter using the **Desearch API**. No aggregators, no stale listings — direct from the source.

![TechJobs Screenshot](https://via.placeholder.com/800x400/0a0a0a/00ff87?text=TechJobs+Dashboard)

## ✨ Features

- **Real-time Job Postings**: Pulls live job postings directly from Twitter
- **Category Filtering**: Browse jobs by category (Engineering, Marketing, Design, Product, Data/ML, DevOps, Sales)
- **Date Range Filtering**: Filter by last 24 hours, 7 days, or 30 days
- **Custom Search**: Add custom keywords to refine your search
- **Modern UI**: Dark-themed, responsive design with smooth animations
- **Direct Links**: Click through to original Twitter posts for full details

## 🏗️ Project Structure

```
Dejobroute-Agent/
├── Backend/
│   ├── main.py           # FastAPI server with Desearch API integration
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Environment variables (API keys)
├── Frontend/
│   └── index.html        # Single-page application with embedded CSS/JS
├── env.example           # Example environment file
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Desearch API](https://console.desearch.ai) API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Dejobroute-Agent
   ```

2. **Set up the Backend**
   ```bash
   cd Backend
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   
   Copy `env.example` to `Backend/.env` and add your Desearch API key:
   ```bash
   # Copy the example file
   cp ../env.example .env
   
   # Edit .env and add your key
   DESEARCH_API_KEY=dt_your_actual_key_here
   ```
   
   > Get your API key from [Desearch Console](https://console.desearch.ai/api-keys)

4. **Start the Backend Server**
   ```bash
   cd Backend
   uvicorn main:app --reload --port 5000
   ```
   The API will be available at `http://localhost:5000`

5. **Open the Frontend**
   
   Simply open `Frontend/index.html` in your browser, or serve it with any static file server.

## 📡 API Reference

### Desearch API Integration

This project uses the **Desearch API** (`https://api.desearch.ai`) to search Twitter for job postings. Desearch is an AI-powered search engine that can query multiple data sources including Twitter/X.

#### API Endpoint Used

```
POST https://api.desearch.ai/desearch/ai/search
```

#### Request Payload

```json
{
  "prompt": "software engineer developer backend frontend fullstack mobile hiring job opening now",
  "tools": ["twitter"],
  "result_type": "LINKS_WITH_FINAL_SUMMARY",
  "count": 40,
  "date_filter": "PAST_WEEK",
  "streaming": true
}
```

#### Request Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Search query/prompt for the AI |
| `tools` | array | Data sources to search (we use `["twitter"]`) |
| `result_type` | string | Type of results (`LINKS_WITH_FINAL_SUMMARY` for summarized results with links) |
| `count` | integer | Number of results to return (10-100) |
| `date_filter` | string | Time range filter (`PAST_24_HOURS`, `PAST_WEEK`, `PAST_MONTH`) |
| `streaming` | boolean | Whether to use streaming SSE response |

#### Headers

| Header | Value |
|--------|-------|
| `Authorization` | Your Desearch API key |
| `Content-Type` | `application/json` |

#### Response Handling

The Desearch API returns a **streaming SSE (Server-Sent Events)** response. The backend parses this response to extract:

1. **Completion events** (`type: "completion"`) - Final summarized content
2. **Text events** (`type: "text"`) - Streaming text chunks

The parsed content is then processed to extract job information from Twitter posts, including:
- Company name
- Role/title
- Tweet text
- Twitter username
- Direct link to the tweet

### Backend API Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{ "status": "TechJobs API running" }
```

#### `GET /api/jobs`
Search for tech jobs on Twitter.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | `all` | Job category filter |
| `date_filter` | string | `7d` | Date range (`24h`, `7d`, `30d`) |
| `query` | string | - | Custom search keywords |
| `count` | integer | `20` | Number of results (10-100) |

**Available Categories:**
- `all` - All tech jobs
- `engineering` - Software engineering roles
- `marketing` - Marketing positions
- `design` - UX/UI/Graphic design roles
- `product` - Product management roles
- `data` - Data science/ML roles
- `devops` - DevOps/Infrastructure roles
- `sales` - Sales positions

**Example Request:**
```bash
curl "http://localhost:5000/api/jobs?category=engineering&date_filter=24h&query=remote"
```

**Response:**
```json
{
  "total": 15,
  "category": "engineering",
  "date_filter": "24h",
  "jobs": [
    {
      "id": "1234567890",
      "role": "Senior Backend Engineer",
      "company": "TechCorp",
      "username": "techcorp",
      "text": "We are hiring a Senior Backend Engineer with experience in Python and microservices...",
      "url": "https://x.com/techcorp/status/1234567890",
      "posted": "Recent"
    }
  ]
}
```

#### `GET /api/categories`
Get list of available job categories.

**Response:**
```json
{
  "categories": ["all", "engineering", "marketing", "design", "product", "data", "devops", "sales"]
}
```

## 🎨 Frontend Features

The frontend is a single-page application built with vanilla HTML, CSS, and JavaScript.

### Design System

- **Color Palette:**
  - Background: `#0a0a0a` (near black)
  - Surface: `#111111` (dark gray)
  - Accent: `#00ff87` (mint green)
  - Accent2: `#00c9ff` (cyan)
  - Text: `#f0f0f0` (off-white)

- **Typography:**
  - Headers: `Syne` (bold, artistic)
  - Body: `Space Mono` (monospace)

### Interactive Elements

- **Category Chips**: Clickable filters for job categories
- **Date Filter Chips**: Toggle between time ranges
- **Search Input**: Custom keyword search with Enter key support
- **Job Cards**: Hover effects with animated accent border
- **Status Bar**: Live indicator showing search status

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client for API calls
- **python-dotenv** - Environment variable management

### Frontend
- **Vanilla HTML/CSS/JS** - No framework dependencies
- **Google Fonts** - Syne & Space Mono typography
- **CSS Variables** - Design system tokens
- **CSS Grid** - Responsive layout

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DESEARCH_API_KEY` | Your Desearch API authentication key | Yes |

### CORS Configuration

The backend is configured to allow CORS from all origins (`*`) for development purposes. For production, update the `allow_origins` list in `Backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Update for production
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## 📝 How It Works

1. **User Interaction**: User selects a category, date filter, and optionally adds custom search terms
2. **API Request**: Frontend sends request to Backend `/api/jobs` endpoint
3. **Prompt Building**: Backend constructs a search prompt based on category and custom query
4. **Desearch API Call**: Backend calls Desearch API with Twitter as the data source
5. **Stream Parsing**: Backend parses the SSE streaming response to extract completion text
6. **Job Extraction**: Regular expressions extract job details from Twitter post content
7. **Response**: Backend returns structured job data to frontend
8. **Rendering**: Frontend displays job cards with company, role, and link to original tweet

## 🚧 Error Handling

The application handles various error scenarios:

- **Missing API Key**: Returns 500 error with instructions
- **Connection Errors**: Returns 503 error if Desearch is unreachable
- **API Errors**: Returns the Desearch error status and message
- **Empty Responses**: Returns 502 error suggesting to retry

## 🔒 Security Notes

- **API Key Security**: Never commit your `.env` file. The `env.example` is provided as a template.
- **CORS**: Currently allows all origins for development. Restrict in production.
- **Input Validation**: Backend validates query parameters and sanitizes output.

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🙏 Acknowledgments

- [Desearch](https://desearch.ai) - AI-powered search API
- [Twitter/X](https://twitter.com) - Real-time job posting source
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python framework

---

**Built with ❤️ using Desearch × Twitter**