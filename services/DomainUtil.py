_EXCLUDED_SITES = []
with open("data/top-sites.txt") as f:
    _EXCLUDED_SITES = _EXCLUDED_SITES + f.readlines()

def is_excluded_domain(domain: str) -> bool:
    if "//" in domain:
        domain = domain.split("//")[1]
    if "/" in domain:
        domain = domain.split("/")[0]
    for excluded in _EXCLUDED_SITES:
        if domain.endswith(excluded):
            return True
    return False