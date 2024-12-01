"""
Quick and dirty setup for managing Groq models. Handles API key, model selection, 
and conversation history config. Uses Groq and AsyncGroq clients.
"""

import base64
import os
import random
import sys
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from groq import APIError, AsyncGroq, BadRequestError, Groq

from errors.model import ModelError
from history import CompletionHistory


class AvailableGroqModels(Enum):
    """
    Enum for the Groq models. Add more here as needed.
    """

    DEFAULT = "llama3-8b-8192"  # General-purpose model
    LARGE = "llama-3.1-70b-versatile"  # Big one for more complex tasks
    VISION = "llama-3.2-11b-vision-preview"  # Image-focused
    TOOL_USE = "llama3-groq-8b-8192-tool-use-preview"  # Tool-helper
    TOOL_USE_LARGE = "llama3-groq-70b-8192-tool-use-preview"  # Bigger tool-helper


class Model:
    """
    Handles setting up a Groq model client. Can be async or sync, depends on what you pass in.
    Tracks some history stuff too.
    """

    def __init__(
        self,
        asynchronous: bool = False,
        history_directory: str = "conversations",
        history_interval_hours: int = 6,
        llm_model: str = AvailableGroqModels.DEFAULT,
    ) -> None:
        """
        Sets up the model client. Exits hard if the API key isn't set.

        Args:
            asynchronous (bool): Use async client if True, sync otherwise.
            history_directory (str): Where to dump history files. Defaults to 'conversations'.
            history_interval_hours (int): How often to rotate history files. Defaults to 6 hours.
            llm_model (str): Which Groq model to use. Defaults to DEFAULT.
        """
        self.api_key = os.environ.get("GROQ_SECRET_KEY")
        if not self.api_key:
            print(ModelError.NO_API_KEY)
            sys.exit(1)  # Hard exit, no API key = no fun

        self.client: Groq | AsyncGroq = Groq() if not asynchronous else AsyncGroq()

        self.model = llm_model
        self.history_directory = history_directory
        self.history_interval_hours = history_interval_hours

        self.history = CompletionHistory(
            debug=True,
            history_directory=self.history_directory,
            new_history_interval=timedelta(self.history_interval_hours),
        )

        self.model_awaiting_confirmation = False
        self.model_deny_words = [
            "no",
            "nope",
            "nah",
            "nevermind",
            "deny",
        ]  # if these aren't found in the response, assume it's a yes.

    def completion(
        self,
        question: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        additional_context: Optional[str] = None,
        code: bool = False,
        image_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generates a response based on the model type and input parameters.

        - question (str): The user's input question or prompt.
        - tools (list of dict, optional): List of tools with their names and parameters.
        - additional_context (str, optional): Additional context for the model.
        - code (str, optional): Prefilled code snippet for code generation tasks.
        - image_path (str, optional): Path to an image file for vision models.
        - Returns (str | None): The generated response or None if an error occurs.

        `usage`:
        ```python


          # Basic Text Completions

          model = Model(llm_model=AvailableGroqModels.DEFAULT)
          answer = model.generate_answer("What is the capital of France?")
          print(answer)


        ```
        ---
        ```python


          # Using Tools

          tools = [
              {
                  "tool_name": "get_weather",
                  "description": "Fetch weather for a specific location.",
                  "tool_parameters": [
                      {
                        "name": "location",
                        "type": "string",
                        "description": "City name",
                        "required": True
                      },
                      {
                        "name": "unit",
                        "type": "string",
                        "description": "Celsius or Fahrenheit",
                        "required": False
                      },
                  ],
              }
          ]

          model = Model(llm_model=AvailableGroqModels.TOOL_USE)
          answer = model.generate_answer(
              question="What's the weather in New York?",
              tools=tools,
              additional_context="Provide detailed weather information.",
          )

          print(answer)


        ```
        ---
        ```python


          # Using a vision model with an image

          model = Model(llm_model=AvailableGroqModels.VISION)
          answer = model.generate_answer(
              question="What do you see in this image?",
              image_path="/path/to/image.jpg",
          )
          print(answer)


        ```
        """
        try:
            messages = [{"role": "user", "content": question}]

            if additional_context:
                messages.insert(0, {"role": "system", "content": additional_context})

            if code:
                messages.append(
                    {"role": "assistant", "content": "```"}
                )  # Gonna use prompt prefilling to force the model to spit out code output only

            prepared_tools = []
            if tools:
                for tool in tools:
                    prepared_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["tool_name"],
                            "description": tool.get("description", ""),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    param["name"]: {
                                        "type": param["type"],
                                        "description": param.get("description", ""),
                                    }
                                    for param in tool.get("tool_parameters", [])
                                },
                                "required": [
                                    param["name"]
                                    for param in tool.get("tool_parameters", [])
                                    if param.get("required", False)
                                ],
                            },
                        },
                    }
                    prepared_tools.append(prepared_tool)

            if (
                self.model
                in {AvailableGroqModels.VISION, AvailableGroqModels.TOOL_USE_LARGE}
                and image_path
            ):
                with open(image_path, "rb") as img_file:
                    image_data = base64.b64encode(img_file.read()).decode("utf-8")
                messages.append(
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": question,
                        },
                        "attachments": [
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{image_data}",
                            }
                        ],
                    }
                )

            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model.value,
                tools=prepared_tools if prepared_tools else None,
                tool_choice="auto" if prepared_tools else None,
            )

            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            return None

        except BadRequestError as e:
            print(f"Invalid request: {e}")
            return None
        except APIError as e:
            print(f"API error occurred: {e}")
            return None

    def ask(self, text: str = None) -> str:
        """
        Handles user input, checks history for similar requests, and generates responses.

        - text (str): The user's input question or prompt.

        What it does:
        - If the history interval has passed, clears and starts a new history.
        - If awaiting confirmation, checks for deny words or generates a response.
        - Searches conversation history for similar inputs and reuses answers if found.
        - If no history match, offers to generate a new answer and sets confirmation state.
        """

        assert text is None, "Model.ask() was called without input."

        if (
            self.history.updated_at
            and datetime.now() - self.history.updated_at
            >= timedelta(self.history_interval_hours)
        ):
            self.history.save()
            self.history.conversation_history.clear()
            self.history.new()

        text = text.strip()

        if self.model_awaiting_confirmation:
            if any(
                deny_word in text.strip().lower().split()
                for deny_word in self.model_deny_words
            ):
                response = "Okay."
                self.history.conversation_history.append(
                    {"role": "assistant", "content": response}
                )

                self.history.save()
                self.model_awaiting_confirmation = False
                return response
            else:
                response = self.completion(text)
                # TODO: I need a way to tell the model whether or not I want to use tools, or look at an image

                if response:
                    self.history.conversation_history.append(
                        {"role": "assistant", "content": response}
                    )

                    self.history.save()
                    self.model_awaiting_confirmation = False

                    return response

        self.history.conversation_history.append({"role": "user", "content": text})

        found_in_history = self.history.search_by_text(text)

        if found_in_history:

            print(f"model - found similar requests: {", ".join(found_in_history)}")

            found_question = found_in_history[0].get("request")
            found_answer = found_in_history[0].get("answer")

            if found_question and found_answer:
                self.history.conversation_history.append(
                    {"role": "assistant", "content": found_answer}
                )
                self.history.save()
                return found_answer

        # otherwise, we haven't found the question or answer
        response = random.choice(
            [
                "I’m not sure about that one. Want me to generate an answer?",
                "I don’t know yet... should I look it up for you?",
                "Hmm, I don’t have that info right now. Want me to figure it out?",
                "I’m not sure off the top of my head. Should I try generating an answer?",
                "Good question! I don’t know yet—want me to dive in and generate something?",
                "I don’t have the answer handy. Should I find or generate it for you?",
                "I’m blanking on this one... want me to take a shot at generating an answer?",
                "Not sure yet. Should I look into it and generate a response?",
            ]
        )

        self.history.conversation_history.append(
            {"role": "assistant", "content": response}
        )

        self.history.save()

        self.model_awaiting_confirmation = True
        return response
