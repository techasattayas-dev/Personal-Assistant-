# Google Maps Tool — Integration Context for Claude Code

## Overview
A Python tool that connects to Google Maps Platform APIs for location intelligence. Drop this into any Python project with a tool registry pattern.

## Prerequisites
- Google Maps API Key with these APIs enabled in Google Cloud Console:
  - Places API
  - Geocoding API
  - Directions API
  - Distance Matrix API
  - Maps Static API
- Python packages: `requests`, `python-dotenv` (no extra Google SDK needed)

## .env Setup
Add this line to your `.env` file:
```
GOOGLE_MAPS_API_KEY=your-api-key-here
```

## File: tools/google_maps.py

```python
"""
Google Maps Tool — Location search, directions, distances, and static maps.

Provides access to Google Maps Platform APIs for:
- Places search (find businesses, landmarks, suppliers by query + location)
- Place details (get address, phone, hours, ratings, website)
- Geocoding (address ↔ coordinates)
- Directions (route between two points with distance/duration)
- Distance Matrix (multiple origin-destination pairs)
- Nearby search (find places within radius of a location)
- Static map image (generate a map image with markers)

Requires GOOGLE_MAPS_API_KEY in .env
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
BASE_URL = "https://maps.googleapis.com/maps/api"


def _check_api_key():
    if not MAPS_API_KEY:
        return "ERROR: GOOGLE_MAPS_API_KEY not found in .env. Add your API key first."
    return None


def _make_request(endpoint: str, params: dict) -> dict:
    """Make a request to Google Maps API."""
    params["key"] = MAPS_API_KEY
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _format_place(place: dict, detailed: bool = False) -> str:
    """Format a place result into readable text."""
    lines = []
    name = place.get("name", "Unknown")
    address = place.get("formatted_address") or place.get("vicinity", "N/A")
    lines.append(f"**{name}**")
    lines.append(f"  Address: {address}")

    if place.get("rating"):
        stars = place["rating"]
        total = place.get("user_ratings_total", 0)
        lines.append(f"  Rating: {stars}/5 ({total} reviews)")

    if place.get("business_status"):
        lines.append(f"  Status: {place['business_status']}")

    if place.get("opening_hours"):
        is_open = place["opening_hours"].get("open_now")
        lines.append(f"  Open now: {'Yes' if is_open else 'No'}")

    if place.get("types"):
        types = [t.replace("_", " ") for t in place["types"][:5]]
        lines.append(f"  Types: {', '.join(types)}")

    if detailed:
        if place.get("formatted_phone_number"):
            lines.append(f"  Phone: {place['formatted_phone_number']}")
        if place.get("international_phone_number"):
            lines.append(f"  Intl Phone: {place['international_phone_number']}")
        if place.get("website"):
            lines.append(f"  Website: {place['website']}")
        if place.get("url"):
            lines.append(f"  Google Maps: {place['url']}")
        if place.get("opening_hours", {}).get("weekday_text"):
            lines.append("  Hours:")
            for day in place["opening_hours"]["weekday_text"]:
                lines.append(f"    {day}")
        if place.get("price_level") is not None:
            price_map = {0: "Free", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
            lines.append(f"  Price level: {price_map.get(place['price_level'], 'N/A')}")

    lat = place.get("geometry", {}).get("location", {}).get("lat")
    lng = place.get("geometry", {}).get("location", {}).get("lng")
    if lat and lng:
        lines.append(f"  Coordinates: {lat}, {lng}")

    return "\n".join(lines)


def google_maps(
    action: str,
    query: str = "",
    location: str = "",
    radius: int = 5000,
    place_id: str = "",
    origin: str = "",
    destination: str = "",
    destinations: list = None,
    origins: list = None,
    mode: str = "driving",
    language: str = "en",
    map_zoom: int = 14,
    map_size: str = "600x400",
    markers: list = None,
    place_type: str = "",
    max_results: int = 10,
) -> str:
    """
    Execute a Google Maps API action.

    Actions:
    - search_places: Text search for businesses/places
    - nearby_search: Find places near a location
    - place_details: Get full details for a place_id
    - geocode: Convert address to coordinates
    - reverse_geocode: Convert coordinates to address
    - directions: Get route between origin and destination
    - distance_matrix: Get distances between multiple origins/destinations
    - static_map: Generate a map image with markers
    """
    err = _check_api_key()
    if err:
        return err

    try:
        if action == "search_places":
            return _search_places(query, location, radius, language, place_type, max_results)
        elif action == "nearby_search":
            return _nearby_search(query, location, radius, language, place_type, max_results)
        elif action == "place_details":
            return _place_details(place_id, language)
        elif action == "geocode":
            return _geocode(query, language)
        elif action == "reverse_geocode":
            return _reverse_geocode(location, language)
        elif action == "directions":
            return _directions(origin, destination, mode, language)
        elif action == "distance_matrix":
            return _distance_matrix(origins or [], destinations or [], mode, language)
        elif action == "static_map":
            return _static_map(location, map_zoom, map_size, markers or [])
        else:
            return (
                f"ERROR: Unknown action '{action}'. Available actions: "
                "search_places, nearby_search, place_details, geocode, "
                "reverse_geocode, directions, distance_matrix, static_map"
            )
    except requests.exceptions.RequestException as e:
        return f"ERROR: Google Maps API request failed: {e}"
    except Exception as e:
        return f"ERROR: {e}"


# ── Action implementations ────────────────────────────────────────────


def _search_places(query, location, radius, language, place_type, max_results):
    """Text search for places (businesses, landmarks, etc.)."""
    if not query:
        return "ERROR: 'query' is required for search_places."

    params = {"query": query, "language": language}
    if location:
        params["location"] = location
        params["radius"] = radius
    if place_type:
        params["type"] = place_type

    data = _make_request("place/textsearch/json", params)

    if data.get("status") != "OK":
        return f"No results found. Status: {data.get('status')}. {data.get('error_message', '')}"

    results = data.get("results", [])[:max_results]
    lines = [f"# Places Search: \"{query}\"", f"Found {len(results)} results:\n"]

    for i, place in enumerate(results, 1):
        lines.append(f"### {i}. {_format_place(place)}")
        lines.append(f"  Place ID: `{place.get('place_id', 'N/A')}`")
        lines.append("")

    lines.append("---")
    lines.append("*Use `place_details` with a Place ID above to get full info (phone, hours, website).*")
    return "\n".join(lines)


def _nearby_search(query, location, radius, language, place_type, max_results):
    """Search for places near a specific location."""
    if not location:
        return "ERROR: 'location' is required for nearby_search. Format: 'lat,lng'"

    params = {"location": location, "radius": radius, "language": language}
    if query:
        params["keyword"] = query
    if place_type:
        params["type"] = place_type

    data = _make_request("place/nearbysearch/json", params)

    if data.get("status") != "OK":
        return f"No results found. Status: {data.get('status')}. {data.get('error_message', '')}"

    results = data.get("results", [])[:max_results]
    lines = [
        f"# Nearby Search (radius: {radius}m)",
        f"Center: {location}",
        f"Found {len(results)} results:\n",
    ]

    for i, place in enumerate(results, 1):
        lines.append(f"### {i}. {_format_place(place)}")
        lines.append(f"  Place ID: `{place.get('place_id', 'N/A')}`")
        lines.append("")

    return "\n".join(lines)


def _place_details(place_id, language):
    """Get detailed information about a specific place."""
    if not place_id:
        return "ERROR: 'place_id' is required. Get it from search_places or nearby_search results."

    params = {
        "place_id": place_id,
        "language": language,
        "fields": (
            "name,formatted_address,formatted_phone_number,international_phone_number,"
            "website,url,opening_hours,rating,user_ratings_total,price_level,"
            "business_status,types,geometry,address_components"
        ),
    }

    data = _make_request("place/details/json", params)

    if data.get("status") != "OK":
        return f"Place not found. Status: {data.get('status')}. {data.get('error_message', '')}"

    place = data.get("result", {})
    lines = ["# Place Details\n", _format_place(place, detailed=True)]

    components = place.get("address_components", [])
    if components:
        lines.append("\n  Address breakdown:")
        for comp in components:
            types = ", ".join(comp.get("types", []))
            lines.append(f"    {comp.get('long_name', '')} ({types})")

    return "\n".join(lines)


def _geocode(query, language):
    """Convert an address to coordinates."""
    if not query:
        return "ERROR: 'query' (address) is required for geocode."

    params = {"address": query, "language": language}
    data = _make_request("geocode/json", params)

    if data.get("status") != "OK":
        return f"Geocoding failed. Status: {data.get('status')}. {data.get('error_message', '')}"

    results = data.get("results", [])
    lines = [f"# Geocoding: \"{query}\"\n"]

    for i, result in enumerate(results[:3], 1):
        loc = result.get("geometry", {}).get("location", {})
        lines.append(f"### Result {i}")
        lines.append(f"  Address: {result.get('formatted_address', 'N/A')}")
        lines.append(f"  Coordinates: {loc.get('lat')}, {loc.get('lng')}")
        lines.append(f"  Place ID: `{result.get('place_id', 'N/A')}`")
        lines.append(f"  Location type: {result.get('geometry', {}).get('location_type', 'N/A')}")
        lines.append("")

    return "\n".join(lines)


def _reverse_geocode(location, language):
    """Convert coordinates to an address."""
    if not location:
        return "ERROR: 'location' (lat,lng) is required for reverse_geocode."

    params = {"latlng": location, "language": language}
    data = _make_request("geocode/json", params)

    if data.get("status") != "OK":
        return f"Reverse geocoding failed. Status: {data.get('status')}. {data.get('error_message', '')}"

    results = data.get("results", [])
    lines = [f"# Reverse Geocoding: {location}\n"]

    for i, result in enumerate(results[:5], 1):
        types = ", ".join(result.get("types", []))
        lines.append(f"### Result {i} ({types})")
        lines.append(f"  Address: {result.get('formatted_address', 'N/A')}")
        lines.append(f"  Place ID: `{result.get('place_id', 'N/A')}`")
        lines.append("")

    return "\n".join(lines)


def _directions(origin, destination, mode, language):
    """Get directions between two points."""
    if not origin or not destination:
        return "ERROR: Both 'origin' and 'destination' are required for directions."

    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "language": language,
        "alternatives": "true",
    }

    data = _make_request("directions/json", params)

    if data.get("status") != "OK":
        return f"Directions failed. Status: {data.get('status')}. {data.get('error_message', '')}"

    routes = data.get("routes", [])
    lines = [
        f"# Directions",
        f"From: {origin}",
        f"To: {destination}",
        f"Mode: {mode}",
        f"Routes found: {len(routes)}\n",
    ]

    for ri, route in enumerate(routes, 1):
        summary = route.get("summary", "N/A")
        legs = route.get("legs", [])

        for leg in legs:
            dist = leg.get("distance", {}).get("text", "N/A")
            dur = leg.get("duration", {}).get("text", "N/A")
            start = leg.get("start_address", "N/A")
            end = leg.get("end_address", "N/A")

            lines.append(f"### Route {ri}: {summary}")
            lines.append(f"  Distance: {dist}")
            lines.append(f"  Duration: {dur}")
            lines.append(f"  Start: {start}")
            lines.append(f"  End: {end}")

            if leg.get("duration_in_traffic"):
                lines.append(f"  Duration (traffic): {leg['duration_in_traffic']['text']}")

            steps = leg.get("steps", [])
            if steps:
                lines.append(f"  Steps ({len(steps)}):")
                for si, step in enumerate(steps, 1):
                    instruction = step.get("html_instructions", "")
                    import re
                    instruction = re.sub(r"<[^>]+>", " ", instruction).strip()
                    step_dist = step.get("distance", {}).get("text", "")
                    step_dur = step.get("duration", {}).get("text", "")
                    lines.append(f"    {si}. {instruction} ({step_dist}, {step_dur})")
            lines.append("")

    return "\n".join(lines)


def _distance_matrix(origins, destinations, mode, language):
    """Get distances between multiple origins and destinations."""
    if not origins or not destinations:
        return "ERROR: Both 'origins' and 'destinations' lists are required for distance_matrix."

    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "mode": mode,
        "language": language,
    }

    data = _make_request("distancematrix/json", params)

    if data.get("status") != "OK":
        return f"Distance matrix failed. Status: {data.get('status')}. {data.get('error_message', '')}"

    origin_addrs = data.get("origin_addresses", [])
    dest_addrs = data.get("destination_addresses", [])
    rows = data.get("rows", [])

    lines = [
        f"# Distance Matrix ({mode})",
        f"Origins: {len(origin_addrs)} | Destinations: {len(dest_addrs)}\n",
    ]

    header = "| From \\ To |"
    separator = "|---|"
    for d in dest_addrs:
        short_d = d[:30] + "..." if len(d) > 30 else d
        header += f" {short_d} |"
        separator += "---|"
    lines.append(header)
    lines.append(separator)

    for i, row in enumerate(rows):
        origin_name = origin_addrs[i][:25] + "..." if len(origin_addrs[i]) > 25 else origin_addrs[i]
        row_str = f"| {origin_name} |"
        for element in row.get("elements", []):
            if element.get("status") == "OK":
                dist = element["distance"]["text"]
                dur = element["duration"]["text"]
                row_str += f" {dist} / {dur} |"
            else:
                row_str += f" {element.get('status', 'N/A')} |"
        lines.append(row_str)

    lines.append("\n*Format: distance / duration*")
    return "\n".join(lines)


def _static_map(location, zoom, size, markers):
    """Generate a static map image and save it."""
    if not location and not markers:
        return "ERROR: Either 'location' (center) or 'markers' are required for static_map."

    params = {"size": size, "zoom": zoom, "maptype": "roadmap", "key": MAPS_API_KEY}

    if location:
        params["center"] = location

    marker_strs = []
    for m in markers:
        if isinstance(m, str):
            marker_strs.append(f"markers={m}")
        elif isinstance(m, dict):
            label = m.get("label", "")
            color = m.get("color", "red")
            loc = m.get("location", "")
            marker_strs.append(f"markers=color:{color}|label:{label}|{loc}")

    url = f"{BASE_URL}/staticmap?{requests.compat.urlencode(params)}"
    for ms in marker_strs:
        url += f"&{ms}"

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    if resp.headers.get("content-type", "").startswith("image"):
        tmp_dir = Path(".tmp")
        tmp_dir.mkdir(exist_ok=True)

        import hashlib
        name_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"map_{name_hash}.png"
        filepath = tmp_dir / filename

        with open(filepath, "wb") as f:
            f.write(resp.content)

        return (
            f"# Static Map Generated\n"
            f"Saved to: `{filepath}`\n"
            f"Center: {location or 'auto'}\n"
            f"Zoom: {zoom}\n"
            f"Size: {size}\n"
            f"Markers: {len(markers)}"
        )
    else:
        return f"ERROR: Unexpected response from Static Maps API. Content-Type: {resp.headers.get('content-type')}"
```

## Tool Registry Entry

Add this import and handler registration:

```python
# Import
from tools.google_maps import google_maps

# Add to _HANDLERS dict
"google_maps": google_maps,
```

## Claude API Tool Definition (for agent tool_use)

Add this to your `TOOL_DEFINITIONS` list:

```python
{
    "name": "google_maps",
    "description": (
        "Access Google Maps Platform APIs for location intelligence. "
        "Actions: 'search_places' (text search for businesses/places), "
        "'nearby_search' (find places near coordinates), "
        "'place_details' (full info: phone, hours, website for a place_id), "
        "'geocode' (address → coordinates), "
        "'reverse_geocode' (coordinates → address), "
        "'directions' (route with distance/duration between two points), "
        "'distance_matrix' (distances between multiple origins/destinations), "
        "'static_map' (generate map image with markers). "
        "Useful for: finding suppliers, logistics planning, branch location analysis, "
        "competitor mapping, delivery route optimization."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "search_places", "nearby_search", "place_details",
                    "geocode", "reverse_geocode", "directions",
                    "distance_matrix", "static_map",
                ],
                "description": "The Google Maps action to perform.",
            },
            "query": {
                "type": "string",
                "description": (
                    "Search query or address. Used by: search_places (e.g. 'restaurants in Bangkok'), "
                    "nearby_search (keyword filter), geocode (address to convert)."
                ),
            },
            "location": {
                "type": "string",
                "description": (
                    "Location as 'lat,lng' (e.g. '13.7563,100.5018' for Bangkok) or address string. "
                    "Used by: search_places (center point), nearby_search (required center), "
                    "reverse_geocode (required), static_map (map center)."
                ),
            },
            "radius": {
                "type": "integer",
                "description": "Search radius in meters (default: 5000). Max: 50000. Used by search_places, nearby_search.",
            },
            "place_id": {
                "type": "string",
                "description": "Google Place ID from search results. Required for place_details action.",
            },
            "origin": {
                "type": "string",
                "description": "Starting point (address or lat,lng). Required for directions.",
            },
            "destination": {
                "type": "string",
                "description": "End point (address or lat,lng). Required for directions.",
            },
            "origins": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of origin addresses/coordinates. Required for distance_matrix.",
            },
            "destinations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of destination addresses/coordinates. Required for distance_matrix.",
            },
            "mode": {
                "type": "string",
                "enum": ["driving", "walking", "bicycling", "transit"],
                "description": "Travel mode (default: driving). Used by directions, distance_matrix.",
            },
            "language": {
                "type": "string",
                "description": "Response language code (default: 'en'). Use 'th' for Thai.",
            },
            "place_type": {
                "type": "string",
                "description": (
                    "Filter by place type (e.g. 'restaurant', 'supermarket', 'store', "
                    "'food', 'veterinary_care', 'gas_station'). Used by search_places, nearby_search."
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Max number of results to return (default: 10, max: 20).",
            },
            "map_zoom": {
                "type": "integer",
                "description": "Map zoom level 1-20 (default: 14). Used by static_map.",
            },
            "map_size": {
                "type": "string",
                "description": "Map image size as 'WxH' (default: '600x400'). Used by static_map.",
            },
            "markers": {
                "type": "array",
                "items": {"type": "object"},
                "description": (
                    "Map markers for static_map. Each marker: "
                    "{'location': 'lat,lng or address', 'label': 'A', 'color': 'red'}."
                ),
            },
        },
        "required": ["action"],
    },
},
```

## Quick Integration Checklist

1. [ ] Copy `tools/google_maps.py` into your project's tools directory
2. [ ] Add `GOOGLE_MAPS_API_KEY=your-key` to `.env`
3. [ ] Add import + handler to your tool registry
4. [ ] Add tool definition to your `TOOL_DEFINITIONS` list
5. [ ] Ensure `requests` and `python-dotenv` are in `requirements.txt`
6. [ ] Enable APIs in Google Cloud Console: Places, Geocoding, Directions, Distance Matrix, Maps Static

## 8 Available Actions — Quick Reference

| Action | Required Params | Returns |
|--------|----------------|---------|
| `search_places` | `query` | Business list with names, addresses, ratings, place IDs |
| `nearby_search` | `location` (lat,lng) | Places within radius of coordinates |
| `place_details` | `place_id` | Full info: phone, hours, website, ratings |
| `geocode` | `query` (address) | Coordinates (lat, lng) |
| `reverse_geocode` | `location` (lat,lng) | Address from coordinates |
| `directions` | `origin`, `destination` | Route with distance, duration, turn-by-turn |
| `distance_matrix` | `origins[]`, `destinations[]` | Distance/duration table for all pairs |
| `static_map` | `location` or `markers` | PNG map image saved to .tmp/ |

## Cost (Google Maps $200 free credit/month)

| API | Cost per request |
|-----|-----------------|
| Places search | $0.032 |
| Place details | $0.017 |
| Geocoding | $0.005 |
| Directions | $0.01 |
| Distance Matrix | $0.01 per element |
| Static Maps | $0.002 |
