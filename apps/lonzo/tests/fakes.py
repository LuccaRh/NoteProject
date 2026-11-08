# Imports
import json
from uuid import UUID, uuid4

import httpx2


# Global variables
# The user Caddy would send in X-User-Id
USER = UUID("00000000-0000-7000-8000-000000000001")
OTHER_USER = UUID("00000000-0000-7000-8000-000000000002")


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
            title = request.url.params.get("title")
            rows = [r for r in self.rows.values() if r["parent_id"] == parent]
            rows = [r for r in rows if title is None or r["title"] == title]

            return httpx2.Response(200, json=rows)

        if request.method == "GET" and path == "/notes/by-path":
            row = self.walk(
                parent_id=request.url.params.get("parent_id"),
                path=request.url.params["path"],
            )

            if row is None:
                return httpx2.Response(404, json={"detail": "note not found"})

            return httpx2.Response(200, json=row)

        if request.method == "GET" and path == "/notes/search":
            words = request.url.params["q"].lower().split()
            rows = self.inside(parent_id=request.url.params.get("parent_id"))
            rows = [
                {"id": r["id"], "title": r["title"]}
                for r in rows
                if not r["is_folder"]
                and all(w in f"{r['title']} {r['body']}".lower() for w in words)
            ]

            return httpx2.Response(200, json=rows)

        if request.method == "GET" and path == "/notes/search-titles":
            text = request.url.params["q"].lower()
            rows = self.inside(parent_id=request.url.params.get("parent_id"))
            fields = ("id", "title", "is_folder")
            rows = [
                {field: r[field] for field in fields}
                for r in rows
                if text in str(r["title"]).lower()
            ]

            return httpx2.Response(200, json=rows)

        if request.method == "GET" and path.endswith("/above"):
            target = UUID(path.removeprefix("/notes/").removesuffix("/above"))

            if target not in self.rows:
                return httpx2.Response(404, json={"detail": "note not found"})

            folders: list[str | None] = []
            parent = self.rows[target]["parent_id"]

            while parent is not None:
                folders = [str(parent), *folders]
                parent = self.rows[UUID(str(parent))]["parent_id"]

            found = [
                self.walk(parent_id=folder, path=request.url.params["path"])
                for folder in [None, *folders]
            ]

            return httpx2.Response(200, json=[r for r in found if r])

        if request.method == "GET" and path.endswith("/path"):
            target = UUID(path.removeprefix("/notes/").removesuffix("/path"))
            names = self.path(note_id=target)

            if not names:
                return httpx2.Response(404, json={"detail": "note not found"})

            row = self.rows[target]

            return httpx2.Response(
                200,
                json={
                    "id": str(target),
                    "path": "/".join(names),
                    "is_folder": row["is_folder"],
                },
            )

        if request.method == "GET" and path.startswith("/notes/"):
            row = self.rows.get(UUID(path.removeprefix("/notes/")))

            if row is None:
                return httpx2.Response(404, json={"detail": "note not found"})

            return httpx2.Response(200, json=row)

        if request.method == "PATCH" and path.startswith("/notes/"):
            row = self.rows.get(UUID(path.removeprefix("/notes/")))

            if row is None:
                return httpx2.Response(404, json={"detail": "note not found"})

            row.update(json.loads(request.content))

            return httpx2.Response(200, json=row)

        if request.method == "DELETE" and path.startswith("/notes/"):
            note_id = UUID(path.removeprefix("/notes/"))

            if note_id not in self.rows:
                return httpx2.Response(404, json={"detail": "note not found"})

            inside = self.inside(parent_id=str(note_id))

            for row in [self.rows[note_id], *inside]:
                del self.rows[UUID(str(row["id"]))]

            return httpx2.Response(204)

        if request.method == "POST" and path == "/notes":
            note = json.loads(request.content)
            parent = note.get("parent_id")

            if self.find(parent_id=parent, title=note["title"]) is not None:
                detail = {"detail": "title already in folder"}

                return httpx2.Response(409, json=detail)

            note_id = self.add(
                title=note["title"],
                parent_id=None if parent is None else UUID(parent),
                is_folder=note.get("is_folder", False),
                body=note.get("body", ""),
            )

            return httpx2.Response(201, json=self.rows[note_id])

        return httpx2.Response(404)

    def find(
        self,
        parent_id: str | None,
        title: str,
    ) -> dict[str, object] | None:

        for row in self.rows.values():
            if row["parent_id"] == parent_id and row["title"] == title:
                return row

        return None

    def inside(self, parent_id: str | None) -> list[dict[str, object]]:

        if parent_id is None:
            return list(self.rows.values())

        rows = self.rows.values()
        children = [r for r in rows if r["parent_id"] == parent_id]

        return children + [
            row
            for child in children
            if child["is_folder"]
            for row in self.inside(parent_id=str(child["id"]))
        ]

    def path(self, note_id: UUID) -> list[str]:

        row = self.rows.get(note_id)

        if row is None:
            return []

        parent = row["parent_id"]
        above = [] if parent is None else self.path(note_id=UUID(str(parent)))

        return [*above, str(row["title"])]

    def walk(
        self,
        parent_id: str | None,
        path: str,
    ) -> dict[str, object] | None:

        row = None

        for name in [name for name in path.split("/") if name]:
            row = self.find(parent_id=parent_id, title=name)

            if row is None:
                return None

            parent_id = str(row["id"])

        return row

    def client(self) -> httpx2.AsyncClient:

        transport = httpx2.MockTransport(self.handle)

        return httpx2.AsyncClient(transport=transport, base_url="http://ichiro")


# ichiro down: every request fails to connect
def down(request: httpx2.Request) -> httpx2.Response:

    raise httpx2.ConnectError("connection refused", request=request)


def unreachable() -> httpx2.AsyncClient:

    transport = httpx2.MockTransport(down)

    return httpx2.AsyncClient(transport=transport, base_url="http://ichiro")
