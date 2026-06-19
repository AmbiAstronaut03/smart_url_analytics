import random
from ipaddress import ip_address
from urllib.parse import urlparse


MULTI_PART_PUBLIC_SUFFIXES = {
    "ac.in",
    "co.in",
    "co.uk",
    "com.au",
    "com.br",
    "com.cn",
    "com.mx",
    "com.sg",
    "com.tr",
    "edu.in",
    "gov.in",
    "net.in",
    "org.in",
    "org.uk",
}


def _extract_domain(url):
    cleaned_url = url.strip()

    if not cleaned_url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(cleaned_url)

    if not parsed.netloc:
        parsed = urlparse(f"//{cleaned_url}")

    hostname = parsed.hostname

    if not hostname:
        raise ValueError("Invalid URL")

    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    try:
        ip_address(hostname)
        return hostname
    except ValueError:
        pass

    parts = hostname.split(".")
    suffix = ".".join(parts[-2:])

    if len(parts) >= 3 and suffix in MULTI_PART_PUBLIC_SUFFIXES:
        return parts[-3]

    if len(parts) >= 2:
        return parts[-2]

    return hostname


def analyze_domain(url):
    domain = _extract_domain(url)

    traffic = random.randint(10000, 5000000)
    global_rank = random.randint(1, 100000)
    country_rank = random.randint(1, 50000)
    categories = ["Ecommerce", "Technology", "Education", "News", "Finance"]
    category = random.choice(categories)

    return {
        "domain": domain,
        "traffic": traffic,
        "global_rank": global_rank,
        "country_rank": country_rank,
        "category": category,
    }
