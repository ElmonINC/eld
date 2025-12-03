# Every Celebration - API Documentation

## Base URL
```
https://everycelebration.com/api/
```

## Authentication
Most endpoints are public. User-specific endpoints require authentication via:
- Session authentication (web)
- Token authentication (API clients)

---

## Celebrations Endpoints

### List Celebrations
Get a list of celebrations with optional filtering.

**Endpoint**: `GET /api/celebrations/`

**Query Parameters**:
- `date__gte` - Date from (YYYY-MM-DD)
- `date__lte` - Date to (YYYY-MM-DD)
- `country` - Country code (e.g., US, GB)
- `type` - Celebration type slug
- `importance` - Minimum importance (1-5)
- `is_public_holiday` - Boolean
- `is_global` - Boolean
- `search` - Text search
- `page` - Page number
- `page_size` - Results per page (max 100)

**Example Request**:
```bash
curl "https://everycelebration.com/api/celebrations/?date__gte=2025-01-01&date__lte=2025-01-31&country=US"
```

**Example Response**:
```json
{
  "count": 15,
  "next": "https://everycelebration.com/api/celebrations/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "New Year's Day",
      "slug": "new-years-day-2025-01-01",
      "description": "The first day of the year in the Gregorian calendar.",
      "date": "2025-01-01",
      "end_date": null,
      "celebration_type": {
        "name": "Public Holiday",
        "slug": "public-holiday",
        "icon": "🏛️",
        "color": "#3b82f6"
      },
      "countries": [
        {
          "code": "US",
          "name": "United States",
          "flag_emoji": "🇺🇸"
        }
      ],
      "is_global": true,
      "is_public_holiday": true,
      "is_religious": false,
      "is_fun_quirky": false,
      "importance": 5,
      "days_until": 39,
      "wikipedia_url": "https://en.wikipedia.org/wiki/New_Year%27s_Day",
      "hashtags": ["#NewYearsDay", "#January1"],
      "view_count": 1523,
      "celebration_count": 842
    }
  ]
}
```

---

### Get Celebration Detail
Get detailed information about a specific celebration.

**Endpoint**: `GET /api/celebrations/{slug}/`

**Example Request**:
```bash
curl "https://everycelebration.com/api/celebrations/new-years-day-2025-01-01/"
```

**Example Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "New Year's Day",
  "slug": "new-years-day-2025-01-01",
  "description": "The first day of the year in the Gregorian calendar. Celebrated worldwide with fireworks, parties, and resolutions.",
  "date": "2025-01-01",
  "end_date": null,
  "is_recurring": true,
  "recurrence_rule": "RRULE:FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1",
  "celebration_type": {
    "name": "Public Holiday",
    "slug": "public-holiday",
    "icon": "🏛️",
    "color": "#3b82f6"
  },
  "countries": [
    {
      "code": "US",
      "name": "United States",
      "flag_emoji": "🇺🇸"
    }
  ],
  "is_global": true,
  "is_public_holiday": true,
  "is_religious": false,
  "religion": "",
  "is_fun_quirky": false,
  "importance": 5,
  "wikipedia_url": "https://en.wikipedia.org/wiki/New_Year%27s_Day",
  "external_url": "",
  "image_url": "https://images.unsplash.com/...",
  "hashtags": ["#NewYearsDay", "#January1", "#HappyNewYear"],
  "source_name": "Nager.Date",
  "confidence_score": 0.95,
  "alternative_names": ["New Year", "January 1st", "New Year's"],
  "days_until": 39,
  "is_upcoming": true,
  "view_count": 1523,
  "celebration_count": 842,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-11-20T14:22:00Z"
}
```

---

### Quick Stats
Get quick statistics about celebrations.

**Endpoint**: `GET /api/stats/`

**Example Response**:
```json
{
  "total_celebrations": 12547,
  "countries_count": 195,
  "types_count": 10,
  "upcoming_week": 127,
  "upcoming_month": 543,
  "most_popular": [
    {
      "name": "Christmas Day",
      "date": "2025-12-25",
      "celebration_count": 15420
    }
  ]
}
```


## Countries Endpoints

### List Countries
Get all available countries.

**Endpoint**: `GET /api/countries/`

**Example Response**:
```json
{
  "count": 195,
  "results": [
    {
      "code": "US",
      "name": "United States",
      "flag_emoji": "🇺🇸",
      "celebration_count": 245
    },
    {
      "code": "GB",
      "name": "United Kingdom",
      "flag_emoji": "🇬🇧",
      "celebration_count": 198
    }
  ]
}
```


## Types Endpoints

### List Celebration Types
Get all celebration types/categories.

**Endpoint**: `GET /api/types/`

**Example Response**:
```json
{
  "count": 10,
  "results": [
    {
      "name": "Public Holiday",
      "slug": "public-holiday",
      "description": "Official government holidays",
      "color": "#3b82f6",
      "icon": "🏛️",
      "celebration_count": 3421
    },
    {
      "name": "Fun & Quirky",
      "slug": "fun-quirky",
      "description": "Fun and unusual celebration days",
      "color": "#f97316",
      "icon": "🎉",
      "celebration_count": 1876
    }
  ]
}
```


## User Endpoints (Authenticated)

### Get My Celebrations
Get current user's personal calendar.

**Endpoint**: `GET /api/me/celebrations/`

**Authentication**: Required

**Example Response**:
```json
{
  "count": 15,
  "results": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174999",
      "celebration": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Pi Day",
        "date": "2025-03-14"
      },
      "is_custom": false,
      "custom_name": null,
      "custom_date": null,
      "reminder_enabled": true,
      "reminder_days_before": 1,
      "notes": "Order pizza!",
      "added_at": "2024-11-01T10:30:00Z"
    }
  ]
}
```

### Add to My Calendar
Add a celebration to user's calendar.

**Endpoint**: `POST /api/me/celebrations/`

**Authentication**: Required

**Request Body**:
```json
{
  "celebration_id": "123e4567-e89b-12d3-a456-426614174000",
  "reminder_enabled": true,
  "reminder_days_before": 1,
  "notes": "Order pizza!"
}
```

**Response**: `201 Created`

### Create Custom Celebration
Create a personal custom celebration.

**Endpoint**: `POST /api/me/celebrations/custom/`

**Authentication**: Required

**Request Body**:
```json
{
  "custom_name": "Mom's Birthday",
  "custom_date": "2025-06-15",
  "custom_description": "Don't forget the cake!",
  "reminder_enabled": true,
  "reminder_days_before": 7
}
```

**Response**: `201 Created`

### Remove from Calendar
Remove a celebration from user's calendar.

**Endpoint**: `DELETE /api/me/celebrations/{id}/`

**Authentication**: Required

**Response**: `204 No Content`

---

## iCal Feed

### Get Personal iCal Feed
Get user's iCal feed for calendar sync.

**Endpoint**: `GET /feed/{secret_key}/`

**Authentication**: None (uses secret key)

**Response**: iCalendar format

**Example**:
```
https://everycelebration.com/feed/123e4567-e89b-12d3-a456-426614174abc/
```

Subscribe in:
- **Google Calendar**: Settings → Add calendar → From URL
- **Apple Calendar**: File → New Calendar Subscription
- **Outlook**: Add calendar → From internet

---

## Search Endpoint

### Search Celebrations
Full-text search across celebrations.

**Endpoint**: `GET /api/search/`

**Query Parameters**:
- `q` - Search query (required)
- `date__gte` - Optional date filter
- `date__lte` - Optional date filter

**Example Request**:
```bash
curl "https://everycelebration.com/api/search/?q=christmas"
```

**Example Response**:
```json
{
  "count": 12,
  "results": [
    {
      "id": "...",
      "name": "Christmas Day",
      "date": "2025-12-25",
      "description": "Christian holiday celebrating...",
      "relevance_score": 0.95
    }
  ]
}
```

---

## Random/Surprise Endpoint

### Get Random Celebration
Get a random upcoming celebration.

**Endpoint**: `GET /api/surprise/`

**Query Parameters**:
- `days_ahead` - Look ahead N days (default: 365)
- `fun_only` - Only return fun/quirky celebrations (boolean)

**Example Response**:
```json
{
  "id": "...",
  "name": "National Pizza Day",
  "date": "2025-02-09",
  "description": "A day to celebrate pizza!",
  "is_fun_quirky": true,
  "days_until": 78
}
```

---

## Rate Limits

- **Anonymous**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Burst**: 10 requests per second

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1635724800
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid date format. Use YYYY-MM-DD",
  "code": "invalid_format"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "code": "authentication_required"
}
```

### 404 Not Found
```json
{
  "error": "Celebration not found",
  "code": "not_found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded. Try again in 60 seconds.",
  "code": "rate_limit_exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error. Please try again later.",
  "code": "internal_error"
}
```

---

## Bulk Export

### Export Celebrations
Export filtered celebrations as CSV.

**Endpoint**: `GET /api/export/csv/`

**Query Parameters**: Same as list endpoint

**Response**: CSV file

**Example**:
```bash
curl "https://everycelebration.com/api/export/csv/?country=US&date__gte=2025-01-01" \
  -o celebrations.csv
```

---

## 🔔 Webhooks (Coming Soon)

Subscribe to celebration events:
- `celebration.created` - New celebration added
- `celebration.updated` - Celebration details changed
- `user.celebration.added` - User adds celebration to calendar

---

## 💡 Usage Examples

### Python
```python
import requests

# Get upcoming celebrations
response = requests.get(
    'https://everycelebration.com/api/celebrations/',
    params={
        'date__gte': '2025-01-01',
        'date__lte': '2025-01-31',
        'country': 'US'
    }
)
celebrations = response.json()['results']

# Add to calendar (authenticated)
session = requests.Session()
session.headers.update({'Authorization': 'Token YOUR_TOKEN'})

response = session.post(
    'https://everycelebration.com/api/me/celebrations/',
    json={
        'celebration_id': '123e4567-e89b-12d3-a456-426614174000',
        'reminder_enabled': True
    }
)
```

### JavaScript
```javascript
// Get celebrations
const response = await fetch(
  'https://everycelebration.com/api/celebrations/?date__gte=2025-01-01'
);
const data = await response.json();
console.log(data.results);

// Add to calendar
const addResponse = await fetch(
  'https://everycelebration.com/api/me/celebrations/',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token YOUR_TOKEN'
    },
    body: JSON.stringify({
      celebration_id: '123e4567-e89b-12d3-a456-426614174000',
      reminder_enabled: true
    })
  }
);
```

### CURL
```bash
# Get celebrations
curl -X GET "https://everycelebration.com/api/celebrations/" \
  -H "Accept: application/json"

# Add to calendar (authenticated)
curl -X POST "https://everycelebration.com/api/me/celebrations/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "celebration_id": "123e4567-e89b-12d3-a456-426614174000",
    "reminder_enabled": true
  }'
```


## Best Practices

1. **Cache responses** - Use ETags and cache headers
2. **Paginate** - Don't request all results at once
3. **Filter intelligently** - Use date ranges to reduce load
4. **Respect rate limits** - Implement exponential backoff
5. **Use compression** - Accept gzip encoding
6. **Handle errors gracefully** - Check status codes

---

##  Support

- **Documentation**: https://docs.everycelebration.com
- **Email**: api@everycelebration.com
- **GitHub**: https://github.com/everycelebration/api-issues

---

**Happy Celebrating!**