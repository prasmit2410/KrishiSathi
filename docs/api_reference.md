# API Reference - Krishi Sathi Phase 1

## Base URL

```
http://localhost:5000/api/v1
```

## Endpoints

### 1. Get Recommendations

**POST** `/recommendations`

Submit farmer inputs and receive crop recommendations.

#### Request

```json
{
  "state": "Maharashtra",
  "district": "Pune",
  "village": "Hadapsar",
  "land_area": 2.0,
  "land_unit": "acres",
  "soil_type": "Black",
  "season": "Kharif",
  "irrigation_available": true
}
```

#### Response (200 OK)

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "farmer_inputs": {
    "state": "Maharashtra",
    "district": "Pune",
    "village": "Hadapsar",
    "land_area": 2.0,
    "land_unit": "acres",
    "soil_type": "Black",
    "season": "Kharif",
    "irrigation_available": true
  },
  "recommendations": [
    {
      "rank": 1,
      "crop_name": "Soybean",
      "suitability": "High",
      "suitability_score": 0.87,
      "estimated_risk": "Low",
      "estimated_return_potential": "High",
      "explanation": "Soybean thrives in black soil with good drainage. Pune district shows strong historical soybean yields during Kharif with adequate irrigation."
    },
    {
      "rank": 2,
      "crop_name": "Cotton",
      "suitability": "High",
      "suitability_score": 0.82,
      "estimated_risk": "Medium",
      "estimated_return_potential": "High",
      "explanation": "Cotton is well-suited to black soil in this region. Market demand is historically strong, though pest management requires attention."
    }
  ],
  "summary": "Based on your 2-acre black soil farm in Pune, Maharashtra, soybean is the top recommendation for Kharif season with irrigation.",
  "metadata": {
    "model_version": "crop_rec_v1.0",
    "agent_execution_id": "exec-abc123",
    "tools_called": ["get_regional_context", "predict_crop_suitability", "validate_recommendations"],
    "llm_model": "openrouter/selected-model",
    "processing_time_ms": 1850,
    "generated_at": "2026-08-14T12:00:00Z"
  },
  "disclaimer": "Recommendations are estimates based on historical patterns and model analysis. Actual results may vary with weather, market conditions, and farming practices. Consult your local Krishi Vigyan Kendra for final decisions."
}
```

#### Error Response (400)

```json
{
  "error": "validation_error",
  "message": "Invalid input",
  "details": {
    "field": "soil_type",
    "value": "InvalidType",
    "allowed_values": ["Black", "Red", "Alluvial", "Laterite", "Sandy", "Clay", "Loamy"]
  }
}
```

### 2. Get Past Recommendation

**GET** `/recommendations/{id}`

Retrieve a previously submitted recommendation by request ID.

#### Response (200 OK)

Returns full recommendation response (same format as POST response).

### 3. List Supported Soil Types

**GET** `/soil-types`

Get list of supported soil types.

#### Response (200 OK)

```json
{
  "soil_types": [
    "Black",
    "Red",
    "Alluvial",
    "Laterite",
    "Sandy",
    "Clay",
    "Loamy"
  ]
}
```

### 4. List States

**GET** `/locations/states`

Get list of supported states.

#### Response (200 OK)

```json
{
  "states": [
    "Maharashtra",
    "Karnataka",
    "Tamil Nadu"
  ]
}
```

### 5. List Districts

**GET** `/locations/districts?state=Maharashtra`

Get list of supported districts for a given state.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| state | string | Yes | State name |

#### Response (200 OK)

```json
{
  "state": "Maharashtra",
  "districts": [
    "Pune",
    "Nashik",
    "Aurangabad",
    "Nagpur",
    "Solapur",
    "Wardha"
  ]
}
```

### 6. Health Check

**GET** `/health`

Check service health status.

#### Response (200 OK)

```json
{
  "status": "healthy",
  "timestamp": "2026-08-14T12:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "ml_model": "loaded"
}
```

## Error Codes

| Code | Description | Example |
|------|-------------|---------|
| 400 | Bad Request - Invalid input | Missing required field or invalid value |
| 404 | Not Found | Recommendation ID doesn't exist |
| 422 | Unprocessable Entity - Processing failed | ML model error, agent timeout |
| 500 | Internal Server Error | Database error, unexpected exception |
| 504 | Gateway Timeout | Agent execution exceeded timeout |

## Input Validation

### Required Fields

- `state` (string): State name, must be in supported list
- `district` (string): District name, must belong to selected state
- `land_area` (float): > 0, max 500
- `land_unit` (string): "acres" or "hectares"
- `soil_type` (string): Must be in supported soil types

### Optional Fields

- `village` (string): Max 100 characters
- `season` (string): "Kharif", "Rabi", or "Zaid"
- `irrigation_available` (boolean): true or false
- `previous_crop` (string): Name of previously grown crop

## Rate Limiting

Phase 1: No rate limiting implemented.

## CORS

Allowed origins: All (Phase 1 development only)

Phase 1.1 will restrict to frontend domain.

## Authentication

Phase 1: No authentication required.

Phase 6: API key authentication will be added.
