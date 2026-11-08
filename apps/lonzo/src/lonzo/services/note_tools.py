# Imports
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from anthropic.lib.tools import BetaAsyncFunctionTool, beta_async_tool

from lonzo.core.connections import ichiro
from lonzo.schemas.notes import Note, NoteMatch, TitleMatch
from lonzo.services.workspaces import (
    find_skill,
    is_skill_path,
    skill_header,
)


# Code
class NoteTools:
    """
    The tools the model uses to find, read, write, edit and delete notes,
    in any folder; new ones go by their whole paths of titles from the
    root, as a coding agent does with files
    """

    created: list[Note]
    titles: dict[str, str]
    folder_id: UUID | None

    def __init__(self, folder_id: UUID | None = None) -> None:
        """
        Tools of a conversation in folder_id, with no note created and no
        title seen yet
        """

        self.folder_id = folder_id
        self.created = []
        self.titles = {}

    def tools(self) -> list[BetaAsyncFunctionTool[Any]]:
        """
        The tools for the tool runner; each docstring below is the
        description the model reads, and the parameters are its schema
        """

        @beta_async_tool(strict=True)
        async def search_notes(
            query: str,
            folder_id: UUID | None = None,
        ) -> str:
            """
            Finds the notes whose title or body has all the words of query
            Whole words only, notes only (not folders), as `id title` lines.
            With folder_id, only inside that folder, at any depth.
            """

            notes = await ichiro.search_notes(query=query, parent_id=folder_id)

            if not notes:
                return "no notes found"

            return self.lines(notes=notes)

        @beta_async_tool(strict=True)
        async def search_titles(
            text: str,
            folder_id: UUID | None = None,
        ) -> str:
            """
            Finds the notes and folders with text anywhere in the title
            Also matches part of a word; folders end in /, as `id title`
            lines. With folder_id, only inside that folder, at any depth.
            """

            notes = await ichiro.search_titles(text=text, parent_id=folder_id)

            if not notes:
                return "no titles found"

            return self.lines(notes=notes)

        @beta_async_tool(strict=True)
        async def list_folder(folder_id: UUID | None = None) -> str:
            """
            Lists what is right inside a folder, or the top level without one
            Folders end in /, as `id title` lines.
            """

            notes = await ichiro.list_notes(parent_id=folder_id)

            if not notes:
                return "the folder is empty"

            return self.lines(notes=notes)

        @beta_async_tool(strict=True)
        async def read_note(note_id: UUID) -> str:
            """
            Reads one note by its id: the title and the whole body
            """

            note = await self.note(note_id=note_id)

            return f"# {note.title}\n\n{note.body}"

        @beta_async_tool(strict=True)
        async def create_note(
            path: str,
            body: str,
        ) -> str:
            """
            Creates a note at its whole path of titles from the root,
            starting with /, e.g. `/Physics/Waves/Summary`. Folders missing
            on the way are created, except the first one. Answers its id.
            """

            self.check_skill(path=path, body=body)
            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders)
            note = await self.create(
                title=title,
                parent_id=parent_id,
                body=body,
            )

            return f"created {note.id} {path}"

        @beta_async_tool(strict=True)
        async def create_folder(path: str) -> str:
            """
            Creates a folder at its whole path of titles from the root,
            starting with /. Folders missing on the way are created too,
            except the first one.
            """

            *folders, title = self.split(path=path)
            parent_id = await self.folder(names=folders)
            await self.create(title=title, parent_id=parent_id, is_folder=True)

            return f"created {path}/"

        @beta_async_tool(strict=True)
        async def edit_note(
            note_id: UUID,
            old_text: str,
            new_text: str,
        ) -> str:
            """
            Changes one piece of a note's body: old_text, copied exactly
            and found only once in the body, becomes new_text (empty to
            remove it). Send only the piece, never the whole note.
            """

            note = await self.note(note_id=note_id)
            count = note.body.count(old_text) if old_text else 0

            if count == 0:
                raise ValueError(f"old_text is not in {note.title}")

            if count > 1:
                raise ValueError(
                    f"old_text is {count} times in {note.title}: send more"
                    " of the text around it"
                )

            body = note.body.replace(old_text, new_text)
            place = await ichiro.get_note_path(note_id=note_id)

            if place is not None:
                self.check_skill(path=place.path, body=body)

            if await ichiro.update_note(note_id=note_id, body=body) is None:
                raise ValueError(f"there is no note {note_id}")

            return f"edited {note.title}"

        @beta_async_tool(strict=True)
        async def delete_note(note_id: UUID) -> str:
            """
            Deletes a note by its id, or a folder with everything inside it
            """

            if not await ichiro.delete_note(note_id=note_id):
                raise ValueError(f"there is no note {note_id}")

            return f"deleted {note_id}"

        @beta_async_tool(strict=True)
        async def load_skill(name: str) -> str:
            """
            Loads a skill of the `# Skills` list by its name: the
            instructions to follow for that task
            """

            skill = await find_skill(folder_id=self.folder_id, name=name)

            if skill is None:
                raise ValueError(f"there is no skill {name}")

            return f"# {skill.title}\n\n{skill.body}"

        return [
            search_notes,
            search_titles,
            list_folder,
            read_note,
            load_skill,
            create_note,
            create_folder,
            edit_note,
            delete_note,
        ]

    async def note(self, note_id: UUID) -> Note:
        """
        The note with note_id; ValueError when it doesn't exist or is a
        folder, whose body the tools don't read nor edit
        """

        note = await ichiro.get_note(note_id=note_id)

        if note is None:
            raise ValueError(f"there is no note {note_id}")

        if note.is_folder:
            raise ValueError(f"{note.title} is a folder: use list_folder")

        return note

    def check_skill(self, path: str, body: str) -> None:
        """
        Refuses a skill note whose header has no description, so the list
        of skills always has a line that says when to use it
        """

        if is_skill_path(path=path) and skill_header(body=body) is None:
            raise ValueError(
                "a skill opens with a header: a --- line, name: <title>,"
                " description: <what it does and when to use it>, a --- line"
            )

    def split(self, path: str) -> list[str]:
        """
        The names along a whole path; ValueError for one that doesn't
        start at the root, is empty or has . or .., which a path of titles
        doesn't have
        """

        if not path.startswith("/"):
            raise ValueError(f"{path} must be a whole path, starting with /")

        names = [name for name in path.split("/") if name]

        if not names:
            raise ValueError("the path is empty")

        if "." in names or ".." in names:
            raise ValueError("the path cannot have . or ..")

        return names

    async def folder(self, names: list[str]) -> UUID | None:
        """
        The folder at the end of names, from the root, creating the ones
        missing; one lookup when it already exists, which is the usual
        case; ValueError when a name on the way is a note, or when the
        first name is missing, which is a mistaken path more often than a
        new folder
        """

        if not names:
            return None

        path = "/".join(names)
        note = await ichiro.get_note_by_path(parent_id=None, path=path)

        if note is None:

            if len(names) == 1:
                raise ValueError(f"there is no folder /{path} at the root")

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
        self.titles[str(note.id)] = note.title

        return note

    def lines(self, notes: Sequence[Note | NoteMatch | TitleMatch]) -> str:
        """
        One `id title` line per note, with a / after the folders; the
        titles stay in titles, since the next tools only get the ids
        """

        self.titles.update({str(note.id): note.title for note in notes})

        return "\n".join(
            f"{note.id} {note.title}{'/' if note.is_folder else ''}"
            for note in notes
        )

    def target(self, tool_input: Mapping[str, object]) -> str | None:
        """
        What a tool call acts on, for the status of the chat: the words
        searched, the name of the skill, the last name of the path or the
        title of the note;
        None while the input is still coming, or for an id never seen
        """

        search = tool_input.get("query") or tool_input.get("text")

        if search is not None:
            return str(search)

        name = tool_input.get("name")

        if name is not None:
            return str(name)

        path = tool_input.get("path")

        if path is not None:
            return str(path).rstrip("/").rsplit("/", 1)[-1]

        note_id = tool_input.get("note_id") or tool_input.get("folder_id")

        return self.titles.get(str(note_id))
