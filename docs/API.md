# API Documentation

This document describes the REST API endpoints available in the Manga Downloader application.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Download Manga

Downloads manga chapters as a ZIP file containing PDFs.

**Endpoint:** `POST /api/manga/download/`

**Request Body:**
```json
{
  "manga_name": "string",
  "chapters": [integer]
}
```

**Parameters:**
- `manga_name` (string, required): The manga name as used on my.ninemanga.com
- `chapters` (array of integers, required): List of chapters to download
  - Empty array `[]`: Download all chapters
  - Single element `[n]`: Download chapter n
  - Two elements `[start, end]`: Download range from start to end

**Response:**
- **Success (200):** Returns a ZIP file containing PDFs of the requested chapters
  - Content-Type: `application/zip`
  - Content-Disposition: `attachment; filename="manga_download.zip"`
  
- **Error (400):** Invalid request data
  ```json
  {
    "error": "Formato de solicitud no válido"
  }
  ```
  or validation errors from the serializer

- **Error (500):** Internal server error
  ```json
  {
    "error": "Error interno del servidor: <error message>"
  }
  ```

**Examples:**

**Download all chapters:**
```bash
curl -X POST http://localhost:8000/api/manga/download/ \
  -H "Content-Type: application/json" \
  -d '{"manga_name": "one-piece", "chapters": []}' \
  --output manga.zip
```

**Download single chapter:**
```bash
curl -X POST http://localhost:8000/api/manga/download/ \
  -H "Content-Type: application/json" \
  -d '{"manga_name": "one-piece", "chapters": [1]}' \
  --output chapter1.zip
```

**Download chapter range:**
```bash
curl -X POST http://localhost:8000/api/manga/download/ \
  -H "Content-Type: application/json" \
  -d '{"manga_name": "one-piece", "chapters": [1, 10]}' \
  --output chapters1-10.zip
```

**Python example:**
```python
import requests

url = "http://localhost:8000/api/manga/download/"
data = {
    "manga_name": "one-piece",
    "chapters": [1, 5]
}

response = requests.post(url, json=data)

if response.status_code == 200:
    with open("manga.zip", "wb") as f:
        f.write(response.content)
    print("Download complete!")
else:
    print(f"Error: {response.json()}")
```

## Web Endpoints (HTML Views)

The following endpoints return HTML pages rather than JSON:

### List All Mangas

**Endpoint:** `GET /manga/list_all_mangas`

**Query Parameters:**
- `title` (string, optional): Filter by title
- `genre` (string, optional): Filter by genre (can be multiple)
- `author` (string, optional): Filter by author
- `start_year` (integer, optional): Filter by minimum release year
- `end_year` (integer, optional): Filter by maximum release year
- `page` (integer, optional): Page number for pagination

**Response:** HTML page with list of mangas

**Example:**
```bash
curl "http://localhost:8000/manga/list_all_mangas?title=one&genre=action"
```

### Manga Details

**Endpoint:** `GET /manga/details/<pk>/`

**Parameters:**
- `pk` (integer, required): Primary key of the manga

**Response:** HTML page with manga details

**Example:**
```bash
curl http://localhost:8000/manga/details/1/
```

### List All Chapters

**Endpoint:** `GET /manga/list_all_chapters/<manga>/`

**Parameters:**
- `manga` (string, required): Manga name as used on my.ninemanga.com

**Response:** HTML page with list of available chapters

**Example:**
```bash
curl http://localhost:8000/manga/list_all_chapters/one-piece/
```

### Populate Database

**Endpoint:** `GET /manga/populate`

**Description:** Populates the database with manga data and creates search index

**Response:** Redirects to list_all_mangas

**Example:**
```bash
curl http://localhost:8000/manga/populate
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

Currently, there is no rate limiting implemented. Consider implementing rate limiting for production use.

## Notes

- The API scrapes data from my.ninemanga.com. Changes to that website may break the API.
- Large downloads may take significant time and memory.
- Ensure you have sufficient disk space for downloaded files.
- The search functionality uses Whoosh index for fast text search.

## Future Enhancements

Potential improvements for the API:

- Add authentication and authorization
- Implement rate limiting
- Add async processing for large downloads
- Provide download status endpoints
- Add webhook notifications for completed downloads
- Implement caching for frequently accessed data
