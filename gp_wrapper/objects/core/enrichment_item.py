import json


class CoreEnrichmentItem:
    def __init__(self, id: str) -> None:
        self.id = id

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {json.dumps(self.__dict__,indent=4)}"
