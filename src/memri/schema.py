from pymemri.data.schema import Account, Edge
from typing import List, Optional


class LinkedInAccount(Account):
    username: str
    locationName: Optional[str] = None


class LinkedInLink(Edge):
    pass
