"""
Isolated AI Agent Engine
------------------------

Standalone demonstration of:
    - Command parsing
    - Intent classification
    - Priority scheduling
    - Tool registry
    - In-memory semantic-style memory
    - Event bus
    - Middleware pipeline
    - Retry mechanism
    - Execution tracing

IMPORTANT:
    This file is completely isolated.
    It does NOT import or access any project modules.
    It does NOT access the filesystem.
    It does NOT use a network connection.
"""

from __future__ import annotations

import asyncio
import time
import uuid
import math

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
)


# ============================================================
# ENUMERATIONS
# ============================================================

class Intent(Enum):
    FILE_OPERATION = auto()
    SYSTEM_OPERATION = auto()
    SEARCH = auto()
    INFORMATION = auto()
    UNKNOWN = auto()


class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AgentState(Enum):
    IDLE = auto()
    ANALYZING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Command:
    text: str
    priority: Priority = Priority.NORMAL
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)


@dataclass
class IntentResult:
    intent: Intent
    confidence: float
    entities: Dict[str, Any]


@dataclass
class ExecutionResult:
    command_id: str
    success: bool
    output: Any
    execution_time: float
    state: AgentState


@dataclass
class TraceEvent:
    timestamp: float
    stage: str
    message: str


# ============================================================
# TOOL PROTOCOL
# ============================================================

class Tool(Protocol):

    @property
    def name(self) -> str:
        ...

    async def execute(self, **kwargs) -> Any:
        ...


# ============================================================
# TOOL REGISTRY
# ============================================================

class ToolRegistry:

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered"
            )

        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        return self._tools[name]

    def available_tools(self) -> List[str]:
        return sorted(self._tools.keys())


# ============================================================
# IN-MEMORY MEMORY ENGINE
# ============================================================

class MemoryEngine:

    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self._records: List[Tuple[str, List[float], Dict[str, Any]]] = []

    def _embed(self, text: str) -> List[float]:
        """
        Deterministic toy embedding.

        This is NOT a real ML embedding model.
        It simply converts characters into a fixed-size vector.
        """

        vector = [0.0] * self.dimension

        for index, char in enumerate(text.lower()):
            position = index % self.dimension
            vector[position] += (ord(char) % 97) / 97.0

        magnitude = math.sqrt(
            sum(value * value for value in vector)
        )

        if magnitude == 0:
            return vector

        return [
            value / magnitude
            for value in vector
        ]

    @staticmethod
    def _cosine_similarity(
        a: List[float],
        b: List[float]
    ) -> float:

        numerator = sum(
            x * y
            for x, y in zip(a, b)
        )

        magnitude_a = math.sqrt(
            sum(x * x for x in a)
        )

        magnitude_b = math.sqrt(
            sum(y * y for y in b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return numerator / (magnitude_a * magnitude_b)

    def store(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:

        embedding = self._embed(text)

        self._records.append(
            (
                text,
                embedding,
                metadata or {}
            )
        )

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:

        query_embedding = self._embed(query)

        scored = []

        for text, embedding, metadata in self._records:

            similarity = self._cosine_similarity(
                query_embedding,
                embedding
            )

            scored.append(
                {
                    "text": text,
                    "similarity": similarity,
                    "metadata": metadata
                }
            )

        scored.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return scored[:top_k]


# ============================================================
# EVENT BUS
# ============================================================

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBus:

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler
    ) -> None:

        self._handlers.setdefault(
            event_name,
            []
        ).append(handler)

    async def publish(
        self,
        event_name: str,
        payload: Dict[str, Any]
    ) -> None:

        handlers = self._handlers.get(
            event_name,
            []
        )

        if not handlers:
            return

        await asyncio.gather(
            *[
                handler(payload)
                for handler in handlers
            ]
        )


# ============================================================
# COMMAND CLASSIFIER
# ============================================================

class CommandClassifier:

    FILE_KEYWORDS = {
        "file",
        "folder",
        "document",
        "directory",
        "pdf",
        "image"
    }

    SYSTEM_KEYWORDS = {
        "shutdown",
        "restart",
        "volume",
        "brightness",
        "process",
        "cpu",
        "memory"
    }

    SEARCH_KEYWORDS = {
        "search",
        "find",
        "look",
        "locate"
    }

    INFORMATION_KEYWORDS = {
        "what",
        "why",
        "how",
        "explain",
        "tell"
    }

    def classify(
        self,
        text: str
    ) -> IntentResult:

        words = set(
            text.lower().split()
        )

        scores = {
            Intent.FILE_OPERATION:
                len(words & self.FILE_KEYWORDS),

            Intent.SYSTEM_OPERATION:
                len(words & self.SYSTEM_KEYWORDS),

            Intent.SEARCH:
                len(words & self.SEARCH_KEYWORDS),

            Intent.INFORMATION:
                len(words & self.INFORMATION_KEYWORDS)
        }

        best_intent = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_intent]

        if best_score == 0:
            return IntentResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
                entities={}
            )

        total = sum(scores.values())

        confidence = (
            best_score / total
            if total > 0
            else 0.0
        )

        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            entities={
                "keywords": list(words)
            }
        )


# ============================================================
# MIDDLEWARE
# ============================================================

class Middleware(Protocol):

    async def process(
        self,
        command: Command,
        next_handler: Callable[[], Awaitable[Any]]
    ) -> Any:
        ...


class LoggingMiddleware:

    async def process(
        self,
        command: Command,
        next_handler: Callable[[], Awaitable[Any]]
    ):

        start = time.perf_counter()

        print(
            f"[LOG] Executing command "
            f"{command.command_id[:8]}"
        )

        result = await next_handler()

        elapsed = (
            time.perf_counter() - start
        )

        print(
            f"[LOG] Completed in "
            f"{elapsed:.4f}s"
        )

        return result


class ValidationMiddleware:

    async def process(
        self,
        command: Command,
        next_handler: Callable[[], Awaitable[Any]]
    ):

        if not command.text.strip():
            raise ValueError(
                "Command cannot be empty"
            )

        if len(command.text) > 500:
            raise ValueError(
                "Command exceeds maximum length"
            )

        return await next_handler()


# ============================================================
# SIMULATED TOOLS
# ============================================================

class CalculatorTool:

    @property
    def name(self) -> str:
        return "calculator"

    async def execute(
        self,
        expression: str
    ) -> Any:

        # Deliberately restricted evaluation.
        allowed = set(
            "0123456789+-*/(). "
        )

        if not set(expression) <= allowed:
            raise ValueError(
                "Unsafe mathematical expression"
            )

        await asyncio.sleep(0.05)

        return eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )


class KnowledgeTool:

    @property
    def name(self) -> str:
        return "knowledge"

    async def execute(
        self,
        question: str
    ) -> str:

        await asyncio.sleep(0.1)

        return (
            f"Simulated knowledge response "
            f"for: '{question}'"
        )


class SystemInfoTool:

    @property
    def name(self) -> str:
        return "system_info"

    async def execute(self) -> Dict[str, Any]:

        await asyncio.sleep(0.05)

        return {
            "cpu_usage": "simulated",
            "memory_usage": "simulated",
            "process_count": 42
        }


# ============================================================
# RETRY ENGINE
# ============================================================

class RetryEngine:

    async def execute(
        self,
        operation: Callable[[], Awaitable[Any]],
        retries: int = 3,
        delay: float = 0.2
    ) -> Any:

        last_error = None

        for attempt in range(1, retries + 1):

            try:
                return await operation()

            except Exception as error:

                last_error = error

                print(
                    f"[RETRY] Attempt "
                    f"{attempt}/{retries} failed: "
                    f"{error}"
                )

                if attempt < retries:
                    await asyncio.sleep(
                        delay * attempt
                    )

        raise last_error


# ============================================================
# PRIORITY QUEUE
# ============================================================

class CommandScheduler:

    def __init__(self):

        self._queue: asyncio.PriorityQueue = (
            asyncio.PriorityQueue()
        )

    async def submit(
        self,
        command: Command
    ) -> None:

        # Negative priority means
        # larger priority runs first.

        await self._queue.put(
            (
                -command.priority.value,
                command.created_at,
                command
            )
        )

    async def next_command(self) -> Command:

        _, _, command = (
            await self._queue.get()
        )

        return command


# ============================================================
# AGENT ENGINE
# ============================================================

class AgentEngine:

    def __init__(self):

        self.classifier = (
            CommandClassifier()
        )

        self.memory = (
            MemoryEngine()
        )

        self.registry = (
            ToolRegistry()
        )

        self.events = (
            EventBus()
        )

        self.scheduler = (
            CommandScheduler()
        )

        self.retry = (
            RetryEngine()
        )

        self.middlewares: List[Middleware] = [
            ValidationMiddleware(),
            LoggingMiddleware()
        ]

        self.state = AgentState.IDLE

        self._register_default_tools()

        self._configure_events()

    # --------------------------------------------------------
    # TOOL SETUP
    # --------------------------------------------------------

    def _register_default_tools(self):

        self.registry.register(
            CalculatorTool()
        )

        self.registry.register(
            KnowledgeTool()
        )

        self.registry.register(
            SystemInfoTool()
        )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    def _configure_events(self):

        async def on_completed(payload):

            print(
                "[EVENT] Command completed:",
                payload["command_id"][:8]
            )

        async def on_failed(payload):

            print(
                "[EVENT] Command failed:",
                payload["command_id"][:8]
            )

        self.events.subscribe(
            "command.completed",
            on_completed
        )

        self.events.subscribe(
            "command.failed",
            on_failed
        )

    # --------------------------------------------------------
    # TRACE
    # --------------------------------------------------------

    def _trace(
        self,
        trace: List[TraceEvent],
        stage: str,
        message: str
    ):

        trace.append(
            TraceEvent(
                timestamp=time.time(),
                stage=stage,
                message=message
            )
        )

    # --------------------------------------------------------
    # COMMAND ROUTING
    # --------------------------------------------------------

    async def _route(
        self,
        command: Command,
        intent: IntentResult,
        trace: List[TraceEvent]
    ):

        self._trace(
            trace,
            "ROUTER",
            f"Intent = {intent.intent.name}"
        )

        text = command.text.strip()

        # -----------------------------------------------
        # Mathematical requests
        # -----------------------------------------------

        if text.startswith("calculate"):

            expression = (
                text[len("calculate"):].strip()
            )

            tool = self.registry.get(
                "calculator"
            )

            return await self.retry.execute(
                lambda: tool.execute(
                    expression=expression
                )
            )

        # -----------------------------------------------
        # System information
        # -----------------------------------------------

        if "system information" in text.lower():

            tool = self.registry.get(
                "system_info"
            )

            return await tool.execute()

        # -----------------------------------------------
        # General information
        # -----------------------------------------------

        tool = self.registry.get(
            "knowledge"
        )

        return await tool.execute(
            question=text
        )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    async def _execute_pipeline(
        self,
        command: Command
    ):

        trace: List[TraceEvent] = []

        self.state = AgentState.ANALYZING

        self._trace(
            trace,
            "ANALYSIS",
