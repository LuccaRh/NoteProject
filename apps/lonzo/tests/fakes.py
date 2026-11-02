# Imports
import json
from uuid import UUID, uuid4

import httpx2


# Code
# Stands in for ichiro: notes kept in a dict, served through httpx2
class FakeIchiro:
    rows: dict[UUID, dict[str, object]]

    def __init__(self) -> None:

        self.rows = {}

    def add(
        self,
        title: str,
        parent_id: UUID | None = None,
        is_folder: bool = False,
        body: str = "",
    ) -> UUID:

        note_id = uuid4()
        self.rows[note_id] = {
            "id": str(note_id),
            "parent_id": None if parent_id is None else str(parent_id),
            "is_folder": is_folder,
            "title": title,
            "body": body,
        }

        return note_id

    def handle(self, request: httpx2.Request) -> httpx2.Response:

        path = request.url.path

        if request.method == "GET" and path == "/notes":
            parent = request.url.params.get("parent_id")
            rows = [r for r in self.rows.values() if r["parent_id"] == parent]

            return httpx2.Response(200, json=rows)

        if request.method == "GET" and path.startswith("/notes/"):
            row = self.rows.get(UUID(path.removeprefix("/notes/")))

            if row is None:
                return httpx2.Response(404, json={"detail": "note not found"})

            return httpx2.Response(200, json=row)

        if request.method == "POST" and path == "/notes":
            note = json.loads(request.content)
            parent = note.get("parent_id")
            note_id = self.add(
                title=note["title"],
                parent_id=None if parent is None else UUID(parent),
                is_folder=note.get("is_folder", False),
                body=note.get("body", ""),
            )

            return httpx2.Response(201, json=self.rows[note_id])

        return httpx2.Response(404)

    def client(self) -> httpx2.AsyncClient:

        transport = httpx2.MockTransport(self.handle)

        return httpx2.AsyncClient(transport=transport, base_url="http://ichiro")
