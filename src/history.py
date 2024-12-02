"""
Handles conversation history. Add stuff, load stuff, search stuff, clear stuff. 
Uses JSON files to store everything, since this'll all be running local anyway
"""

import json
import os
from datetime import datetime, timedelta
from difflib import get_close_matches
from pathlib import Path
from typing import List, Optional, Union


class CompletionHistory:
    """
    Manages conversation history using JSON files. Handles file rotation,
    saving, clearing, loading, searching, and merging history files.
    Each conversation entry follows the format:
    {
        "id": int,
        "model": str,
        "timestamp": datetime,
        "request": str,
        "answer": str
    }
    """

    def __init__(
        self,
        debug: bool = True,
        history_directory: str = "conversations",
        history_file_prefix: str = "c_",
        history_file_extension: str = ".json",
        new_history_interval: timedelta = timedelta(hours=6),
        recent_conversations_to_load: int = -1,
    ) -> None:
        """
        Initializes the history manager. Defaults should work out of the box.
        - debug (bool): Print debug messages if True.
        - history_directory (str): Where to store history files.
        - history_file_prefix (str): Prefix for the history file names.
        - history_file_extension (str): File extension for history files.
        - new_history_interval (timedelta): When to create a new file.
        - recent_conversations_to_load (int): Number of recent conversations to load (-1 for all).
        """
        self.history_directory = history_directory
        self.history_file_prefix = history_file_prefix
        self.history_file_ext = history_file_extension
        self.new_history_interval = new_history_interval
        self.recent_conversations_to_load = recent_conversations_to_load

        self.debug = debug
        self.updated_at: datetime = None
        self.current_history_file: Optional[str] = None
        self.conversation_history: List[dict] = []

        self.timestamp_file = os.path.join(self.history_directory, "h.timestamp")
        self.last_history_time: Optional[datetime] = None

        self.initialize()
        self.load_recent_conversations()
        self.load_last_history_time()

    def initialize(self) -> None:
        """
        Ensures the history directory exists. Creates it if needed.
        """

        os.makedirs(self.history_directory, exist_ok=True)
        if self.debug:
            print("history - initialized conversation directory")

    def _generate_name(self) -> str:
        """
        Generates a unique file name based on the current timestamp.
        - Returns (str): Full path for the new history file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            self.history_directory,
            f"{self.history_file_prefix}{timestamp}{self.history_file_ext}",
        )

    def load_last_history_time(self) -> None:
        """
        Loads the timestamp of the last history file created from 'h.timestamp' file.
        """
        if os.path.exists(self.timestamp_file):
            with open(self.timestamp_file, "r", encoding="UTF-8") as f:
                timestamp_str = f.read()
                self.last_history_time = datetime.fromisoformat(timestamp_str)
        else:
            self.last_history_time = None
            if self.debug:
                print(
                    "history - 'h.timestamp' file not found. No last history time loaded."
                )

    def new(self) -> None:
        """
        Creates a new history file and resets internal references.
        """
        self.updated_at = datetime.now()
        self.current_history_file = self._generate_name()

        with open(self.timestamp_file, "w", encoding="UTF-8") as f:
            f.write(self.updated_at.isoformat())

        self.last_history_time = self.updated_at

        if self.debug:
            print(f"history - created new history file: {self.current_history_file}")

    def save(self) -> None:
        """
        Saves the current conversation history.
        Checks if the new history interval has passed before creating a new file.
        """
        if self.current_history_file is None:
            self.new()
        else:
            # If last_history_time is None or interval has passed, create a new history file
            if (
                self.last_history_time is None
                or datetime.now() - self.last_history_time >= self.new_history_interval
            ):
                self.new()

        with open(self.current_history_file, "w", encoding="UTF-8") as f:
            json.dump(self.conversation_history, f, default=str, indent=4)

    def clear(self) -> None:
        """
        Clears the current conversation history. Resets everything.
        """
        self.conversation_history = []
        self.current_history_file = None
        self.updated_at = datetime.now()

    def load_recent_conversations(self) -> None:
        """
        Loads recent conversations into memory based on the recent_conversations_to_load setting.
        Also sets the current history file to the most recent one.
        """
        files = sorted(
            Path(self.history_directory).glob(f"*{self.history_file_ext}"), reverse=True
        )
        files_to_load = (
            files[: self.recent_conversations_to_load]
            if self.recent_conversations_to_load != -1
            else files
        )

        self.conversation_history = []
        if files_to_load:
            self.current_history_file = str(files_to_load[0])
        else:
            self.current_history_file = None

        for file in files_to_load:
            with open(file, "r", encoding="UTF-8") as f:
                self.conversation_history.extend(json.load(f))
        # if self.conversation_history:
        #     self.next_id = max(entry["id"] for entry in self.conversation_history) + 1
        # else:
        #     self.next_id = 0
        if self.debug:
            print(f"history - loaded {len(self.conversation_history)} conversations")

    def search_by_key(self, key: str, value: Union[str, int]) -> List[dict]:
        """
        Searches for all conversations where a specific key matches the given value.
        - key (str): The key to search by (e.g., 'id', 'model').
        - value (str | int): The value to match.
        - Returns (List[dict]): Matching conversation entries.
        """
        return [entry for entry in self.conversation_history if entry.get(key) == value]

    def search_by_text(self, text: str, cutoff: float = 0.6) -> List[dict]:
        """
        Performs a similarity search for conversations matching the given text.
        - text (str): The text to search for.
        - cutoff (float): Minimum similarity score to consider a match (0-1).
        - Returns (List[dict]): Matching conversation entries based on similarity.
        """
        matches = []
        for entry in self.conversation_history:
            for key in ["request", "answer"]:
                if key in entry and isinstance(entry[key], str):
                    close_matches = get_close_matches(
                        text, [entry[key]], n=1, cutoff=cutoff
                    )
                    if close_matches:
                        matches.append(entry)
                        break
        return matches
