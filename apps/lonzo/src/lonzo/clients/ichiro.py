# Imports
import os
from uuid import UUID

import httpx2
from pydantic import TypeAdapter

from lonzo.errors import TitleTaken
from lonzo.schemas.notes import Note, NoteMatch, NotePath, TitleMatch
from lonzo.user import current_user


# Global variables
ICHIRO_URL = os.environ.get("ICHIRO_URL", "http://ichiro:8000")


# Code
async def add_user(request: httpx2.Request) -> None:
    """
    Sends ichiro the user of the chat request in X-User-Id, so its
    row-level security keeps the chat inside the notes of that user
    """

    user_id = current_user.get()

    if user_id is not None:
        request.headers["X-User-Id"] = str(user_id)


class IchiroClient:
    """
    The notes service, straight through the compose network: one method
    per endpoint, answering the models of schemas/, with no lonzo rules
    """

    http: httpx2.AsyncClient

    def __init__(self) -> None:
        """
        One pool of connections to ichiro, at ICHIRO_URL, each request
        with the user of the chat request
        """

        self.http = httpx2.AsyncClient(
            base_url=ICHIRO_URL,
            event_hooks={"request": [add_user]},
        )

    async def close(self) -> None:
        """
        Closes the connections kept open to ichiro
        """

        await self.http.aclose()

    async def list_notes(
        self,
        parent_id: UUID | None,
        title: str | None = None,
    ) -> list[Note]:
        """
        GET /notes: the notes and folders right inside a folder (None = the
        root), only the one with that title when title is given
        """

        params = {}

        if parent_id is not None:
            params["parent_id"] = str(parent_id)

        if title is not None:
            params["title"] = title

        response = await self.http.get("/notes", params=params)
        response.raise_for_status()

        return TypeAdapter(list[Note]).validate_python(response.json())

    async def get_note(self, note_id: UUID) -> Note | None:
        """
        GET /notes/{id}: one note or folder; None when there is no such note
        """

        response = await self.http.get(f"/notes/{note_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return Note.model_validate(response.json())

    async def get_note_path(self, note_id: UUID) -> NotePath | None:
        """
        GET /notes/{id}/path: the path of titles of a note from the root;
        None when there is no such note
        """

        response = await self.http.get(f"/notes/{note_id}/path")

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return NotePath.model_validate(response.json())

    async def get_note_by_path(
        self,
        parent_id: UUID | None,
        path: str,
    ) -> Note | None:
        """
        GET /notes/by-path: the note or folder at a path of titles (a/b/c)
        inside parent_id (None = the root); None when a name is missing
        """

        params = {"path": path}

        if parent_id is not None:
            params["parent_id"] = str(parent_id)

        response = await self.http.get("/notes/by-path", params=params)

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return Note.model_validate(response.json())

    async def search_notes(
        self,
        query: str,
        parent_id: UUID | None,
    ) -> list[NoteMatch]:
        """
        GET /notes/search: the notes whose title or body has the words of
        query, inside parent_id at any depth (None = all of them)
        """

        params = {"q": query}

        if parent_id is not None:
            params["parent_id"] = str(parent_id)

        response = await self.http.get("/notes/search", params=params)
        response.raise_for_status()

        return TypeAdapter(list[NoteMatch]).validate_python(response.json())

    async def search_titles(
        self,
        text: str,
        parent_id: UUID | None,
    ) -> list[TitleMatch]:
        """
        GET /notes/search-titles: the notes and folders with text anywhere
        in the title, inside parent_id at any depth (None = all of them)
        """

        params = {"q": text}

        if parent_id is not None:
            params["parent_id"] = str(parent_id)

        response = await self.http.get("/notes/search-titles", params=params)
        response.raise_for_status()

        return TypeAdapter(list[TitleMatch]).validate_python(response.json())

    async def create_note(
        self,
        title: str,
        parent_id: UUID | None,
        body: str = "",
        is_folder: bool = False,
    ) -> Note:
        """
        POST /notes: a new note or folder inside parent_id (None = the
        root), as ichiro saved it; TitleTaken when the folder already has
        that title
        """

        note = {
            "title": title,
            "body": body,
            "parent_id": None if parent_id is None else str(parent_id),
            "is_folder": is_folder,
        }
        response = await self.http.post("/notes", json=note)

        if response.status_code == 409:
            raise TitleTaken(f"{title} already exists")

        response.raise_for_status()

        return Note.model_validate(response.json())

    async def update_note(self, note_id: UUID, body: str) -> Note | None:
        """
        PATCH /notes/{id}: the new body of a note, as ichiro saved it;
        None when the note doesn't exist
        """

        response = await self.http.patch(
            f"/notes/{note_id}",
            json={"body": body},
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return Note.model_validate(response.json())

    async def delete_note(self, note_id: UUID) -> bool:
        """
        DELETE /notes/{id}: a note, or a folder with everything inside it;
        False when it doesn't exist
        """

        response = await self.http.delete(f"/notes/{note_id}")

        if response.status_code == 404:
            return False

        response.raise_for_status()

        return True
