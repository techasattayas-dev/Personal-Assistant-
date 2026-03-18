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
        return "ERROR: 'query' is required for search_places. Example: 'pig feed suppliers near Phichit'"

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
        return "ERROR: 'location' is required for nearby_search. Format: 'lat,lng' (e.g. '13.7563,100.5018' for Bangkok)"

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

    # Add address components breakdown
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

            # Step-by-step directions
            steps = leg.get("steps", [])
            if steps:
                lines.append(f"  Steps ({len(steps)}):")
                for si, step in enumerate(steps, 1):
                    instruction = step.get("html_instructions", "")
                    # Strip HTML tags
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

    # Build table header
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

    # Build markers parameter
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

    # Download and save
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
