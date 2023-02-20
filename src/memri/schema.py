from pymemri.data.schema import Account, Edge
from typing import List, Optional


class LinkedInAccount(Account):
    username: str
    location_name: Optional[str] = None


class LinkedInLink(Edge):
    pass
