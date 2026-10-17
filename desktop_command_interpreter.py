from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict
import re


class ActionType(Enum):

    OPEN_APPLICATION = "OPEN_APPLICATION"
    SEARCH_CONTENT = "SEARCH_CONTENT"
    MODIFY_CONTENT = "MODIFY_CONTENT"
    SYSTEM_QUERY = "SYSTEM_QUERY"
    CLOSE_APPLICATION = "CLOSE_APPLICATION"
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedCommand:

    action: ActionType
    target: Optional[str]
    parameters: Dict[str, str]
    confidence: float


class CommandInterpreter:

    APPLICATIONS = {
        "chrome",
        "browser",
        "calculator",
        "notepad",
        "terminal",
        "spotify",
        "vscode"
    }

    def normalize(self, text: str) -> str:

        text = text.lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    def detect_action(
        self,
        text: str
    ) -> ActionType:

        if re.search(
            r"\b(open|launch|start)\b",
            text
        ):
            return ActionType.OPEN_APPLICATION

        if re.search(
            r"\b(find|search|locate)\b",
        ):
            return ActionType.SEARCH_CONTENT

        if re.search(
            text
        ):
            return ActionType.MODIFY_CONTENT

        if re.search(
            text
        ):

        if re.search(
            r"\b(cpu|memory|system|performance)\b",
        ):

        return ActionType.UNKNOWN

            if application in text:
                return application

    def extract_search_query(
        self,
        action = self.detect_action(text)
                confidence = 0.45
                0.92 if target else 0.55
        elif action == ActionType.SYSTEM_QUERY:

            confidence = 0.94
        elif action == ActionType.CLOSE_APPLICATION:
        print("CONFIDENCE:", result.confidence)
            confidence = (
                0.94 if target else 0.50
            )


            target = self.extract_search_query(text)

            confidence = 0.75


            confidence = 0.05

        parameters["original"] = command

        return ParsedCommand(
            action=action,
        print("ACTION:", result.action.value)
        print("TARGET:", result.target)
            target=target,
            parameters=parameters,
            confidence=confidence
        )



        print("\nCOMMAND:", command)
if __name__ == "__main__":

    interpreter = CommandInterpreter()

    commands = [
        "Open Chrome",
        "Find my machine learning notes",
        "Close VSCode",
        "Show system performance",
        "Modify the project documentation"
    ]

    for command in commands:

        result = interpreter.parse(command)
        else:
        elif action == ActionType.MODIFY_CONTENT:
            target = self.extract_application(text)



            target = "system"
            )

            else:

            confidence = (
                confidence = 0.95

        elif action == ActionType.SEARCH_CONTENT:

            target = self.extract_search_query(text)

        if action == ActionType.OPEN_APPLICATION:

            target = self.extract_application(text)

            if target is None:
        target = None

        parameters = {}

            r"search for (.+)",
            match = re.search(

    ) -> ParsedCommand:

        text = self.normalize(command)
        self,
        command: str
                pattern,

    def parse(

        return None

            if match:
                return match.group(1).strip()
                text
            )

        for pattern in patterns:

            r"locate (.+)"
        ]

        patterns = [
            r"find (.+)",
        text: str
    ) -> Optional[str]:
        return None

        for application in self.APPLICATIONS:

        self,

        text: str
    ) -> Optional[str]:
    def extract_application(
            return ActionType.SYSTEM_QUERY
            text
            return ActionType.CLOSE_APPLICATION
            r"\b(close|exit|stop)\b",
            r"\b(edit|modify|change|update)\b",

