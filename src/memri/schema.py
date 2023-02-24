from pymemri.data.schema import Account, Edge
from typing import List, Optional


class LinkedInAccount(Account):
    locationName: Optional[str] = None


class LinkedInLink(Edge):
    pass
