_EXCLUDED_SITES = []
with open("data/top-sites.txt") as f:
    _EXCLUDED_SITES = _EXCLUDED_SITES + f.readlines()

_EXCLUDED_MAILS = []
with open("data/top-email.txt") as f:
    _EXCLUDED_MAILS = _EXCLUDED_MAILS + f.readlines()

def is_excluded_domain(domain: str) -> bool:
    if "//" in domain:
        domain = domain.split("//")[1]
    if "/" in domain:
        domain = domain.split("/")[0]
    for excluded in _EXCLUDED_SITES:
        if domain.endswith(excluded.strip()):
            return True
    return False

def is_excluded_email_domain(domain: str) -> bool:
    if "@" in domain:
        domain = domain.split("@")[1]
    for excluded in _EXCLUDED_MAILS:
        if domain.endswith(excluded.strip()):
            return True
    return False
    