"""GeoIP Resolver with in-memory caching and Cloudflare header prioritization.

Lightweight, non-blocking resolution of country, city, and region/zone for visitor tracking.
"""

import ipaddress
import logging
from typing import Tuple, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# In-memory cache to avoid duplicate lookups for the same IP
_GEO_CACHE: Dict[str, Tuple[str, str, str]] = {}


def is_private_ip(ip_str: str) -> bool:
    """Check if IP is loopback, link-local, or private RFC1918/CGNAT."""
    try:
        ip_obj = ipaddress.ip_address(ip_str.strip())
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved
    except ValueError:
        return False


async def resolve_visitor_location(
    ip: str,
    headers: Dict[str, str] = None,
    client: httpx.AsyncClient = None,
) -> Tuple[str, str, str]:
    """Resolve (country, city, region) for an incoming request.

    Priority:
    1. Cloudflare headers (CF-IPCountry, CF-IPCity, CF-Region)
    2. Private/LAN check
    3. Memory cache
    4. Fast external fallback (ip-api.com) for public IPs
    """
    headers = headers or {}
    clean_ip = ip.strip()

    # 1. Cloudflare native headers
    cf_country = headers.get("cf-ipcountry")
    cf_city = headers.get("cf-ipcity")
    cf_region = headers.get("cf-region") or headers.get("cf-region-code")

    if cf_city or cf_region:
        return (cf_country or "XX", cf_city or "", cf_region or "")

    # 2. Private IP
    if is_private_ip(clean_ip) or clean_ip in ("127.0.0.1", "localhost", "::1"):
        return (cf_country or "LOCAL", "Local", "LAN / Tailscale")

    # 3. Check in-memory cache
    if clean_ip in _GEO_CACHE:
        cached_country, cached_city, cached_region = _GEO_CACHE[clean_ip]
        return (cf_country or cached_country, cached_city, cached_region)

    # 4. Fast external lookup for public IPs
    try:
        url = f"http://ip-api.com/json/{clean_ip}?fields=status,countryCode,regionName,city"
        if client:
            resp = await client.get(url)
            data = resp.json()
        else:
            async with httpx.AsyncClient(timeout=1.0) as temp_client:
                resp = await temp_client.get(url)
                data = resp.json()

        if data.get("status") == "success":
            country = data.get("countryCode") or cf_country or "XX"
            city = data.get("city") or ""
            region = data.get("regionName") or ""
            _GEO_CACHE[clean_ip] = (country, city, region)
            return (country, city, region)
    except Exception as exc:
        logger.debug("GeoIP lookup timed out or failed for %s: %s", clean_ip, exc)

    fallback = (cf_country or "XX", "", "")
    _GEO_CACHE[clean_ip] = fallback
    return fallback
