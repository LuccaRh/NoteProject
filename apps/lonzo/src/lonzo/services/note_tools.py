# Imports
from typing import Any
from uuid import UUID

from anthropic.lib.tools import BetaAsyncFunctionTool, beta_async_tool

from lonzo.connections import ichiro
from lonzo.schemas.notes import Note


# Code
class NoteTools:
    """
    The tools the model uses on the notes, in any folder, by paths of
    titles from a folder (or the root), as a coding agent does with files
    """

    created: list[Note]

    def __init__(self) -> None:
        """
        Tools with no note created yet
        """

        self.created = []

    def tools(self) -> list[BetaAsyncFunctionTool[Any]]:
        """
        The tools for the tool runner; each docstring below is the
        description the model reads, and the parameters are its schema
        """

        @beta_async_tool(strict=True)
        async def create_note(
            path: str,
            body: str,
            folder_id: UUID | None = None,
        ) -> str:
            """
            Creates a note at a path of titles from folder_id (the root
            without one). Folders missing on the way are created, e.g.
            `.workspace/skills/review-report`.
            """

            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders, folder_id=folder_id)
            await self.create(title=title, parent_id=parent_id, body=body)

            return f"created {path}"

        @beta_async_tool(strict=True)
        async def create_folder(
            path: str,
            folder_id: UUID | None = None,
        ) -> str:
            """
            Creates a folder at a path of titles from folder_id (the root
            without one). Folders missing on the way are created too.
            """

            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders, folder_id=folder_id)
            await self.create(title=title, parent_id=parent_id, is_folder=True)

            return f"created {path}/"

        return [create_note, create_folder]

    def split(self, path: str) -> list[str]:
        """
        The names along a path; ValueError for an empty one or one with
        . or .., which a path of titles doesn't have
        """

        names = [name for name in path.split("/") if name]

        if not names:
            raise ValueError("the path is empty")

        if "." in names or ".." in names:
            raise ValueError("the path cannot have . or ..")

        return names

    async def folder(
        self,
        names: list[str],
        folder_id: UUID | None,
    ) -> UUID | None:
        """
        The folder at the end of names, from folder_id, creating the ones
        missing; one lookup when it already exists, which is the usual
        case; ValueError when a name on the way is a note
        """

        if not names:
            return folder_id

        path = "/".join(names)
        note = await ichiro.get_note_by_path(parent_id=folder_id, path=path)

        if note is None:
            parent_id = await self.folder(
                names=names[:-1],
                folder_id=folder_id,
            )
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
        parent_id: UUID | None,
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
