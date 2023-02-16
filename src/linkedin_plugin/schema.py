""" Items to be stored in the pod. """
from typing import Optional
from pymemri.data import schema
from pymemri.data.schema import Item

SERVICE_NAME = "linkedin"


class HashableItem(Item):
    def __hash__(self):
        if self.externalId is None:
            raise ValueError("Cannot hash item without externalId")
        return hash(self.__class__.__name__ + self.externalId)


class Account(HashableItem, schema.Account):
    service: Optional[str] = SERVICE_NAME
    description: Optional[str]
