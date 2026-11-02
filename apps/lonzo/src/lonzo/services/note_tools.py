# Imports
from typing import Any
from uuid import UUID

from anthropic.lib.tools import BetaAsyncFunctionTool, beta_async_tool

from lonzo.connections import ichiro
from lonzo.schemas.notes import Note


# Code
class NoteTools:
    """
    The tools the model uses on the notes of one folder, by paths relative
    to it, as a coding agent does with files; it never leaves that folder
    """

    root_id: UUID
    created: list[Note]

    def __init__(self, root_id: UUID) -> None:
        """
        Tools on the notes inside root_id, the folder of the workspace
        """

        self.root_id = root_id
        self.created = []

    def tools(self) -> list[BetaAsyncFunctionTool[Any]]:
        """
        The tools for the tool runner; each docstring below is the
        description the model reads, and the parameters are its schema
        """

        @beta_async_tool(strict=True)
        async def create_note(path: str, body: str) -> str:
            """
            Creates a note at a path relative to the workspace folder
            Folders missing on the way are created, e.g.
            `.workspace/skills/review-report`.
            """

            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders)
            await self.create(title=title, parent_id=parent_id, body=body)

            return f"created {path}"

        @beta_async_tool(strict=True)
        async def create_folder(path: str) -> str:
            """
            Creates a folder at a path relative to the workspace folder
            Folders missing on the way are created too.
            """

            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders)
            await self.create(title=title, parent_id=parent_id, is_folder=True)

            return f"created {path}/"

        return [create_note, create_folder]

    def split(self, path: str) -> list[str]:
        """
        The names along a path; ValueError for an empty one or one that
        tries to leave the folder
        """

        names = [name for name in path.split("/") if name]

        if not names:
            raise ValueError("the path is empty")

        if "." in names or ".." in names:
            raise ValueError("the path cannot have . or ..")

        return names

    async def folder(self, names: list[str]) -> UUID:
        """
        The folder at the end of names, from the root, creating the ones
        missing; one lookup when it already exists, which is the usual
        case; ValueError when a name on the way is a note
        """

        if not names:
            return self.root_id

        path = "/".join(names)
        note = await ichiro.get_note_by_path(parent_id=self.root_id, path=path)

        if note is None:
            parent_id = await self.folder(names=names[:-1])
            note = await self.create(
                title=names[-1],
                parent_id=parent_id,
                is_folder=True,
            )
        elif not note.is_folder:
            raise ValueError(f"{path} is a note, not a folder")

        return note.id

    async def create(
        self,
        title: str,
        parent_id: UUID,
        body: str = "",
        is_folder: bool = False,
    ) -> Note:
        """
        Saves a new note or folder in ichiro and keeps it in created;
        TitleTaken when the title is already taken there
        """

        note = await ichiro.create_note(
            title=title,
            parent_id=parent_id,
            body=body,
            is_folder=is_folder,
        )
        self.created.append(note)

        return note
