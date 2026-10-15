            print(" -", reason)        print("DECISION:", result.decision.value)

        for reason in result.reasons:
        print("SCORE:", result.score)
        print("RISK:", result.level.name)
        result = engine.assess(action)

        print("\nACTION:", action.name)
from dataclasses import dataclass
            reversible=True,

    for action in actions:

        Action(
            reversible=True,
            affects_data=True,
            external_communication=False
        ),
            external_communication=False
        )
    ]

        Action(
            name="send_message",
            target="external_user",
            reversible=False,
            affects_system=True,
            affects_system=False,
            external_communication=True
        ),

        Action(
            name="system_change",
            target="critical_setting",
            reversible=False,
            affects_data=True,
            affects_data=False,
            affects_system=False,
            name="modify_document",
            target="research.txt",
            affects_data=False,
        ),

            affects_system=False,
            external_communication=False

    engine = SafetyEngine()

        Action(
            name="calculate",
            target="25 * 10",

    actions = [
from enum import Enum
from typing import List


if __name__ == "__main__":


class RiskLevel(Enum):
            decision=decision
        )

    SAFE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


            score=score,
            reasons=reasons,
            level=level,
class Decision(Enum):

    ALLOW = "ALLOW"
    CONFIRM = "REQUIRE_CONFIRMATION"
    DENY = "DENY"


            decision = Decision.ALLOW

        return RiskAssessment(
@dataclass
class Action:

    name: str
    target: str
    reversible: bool
    affects_data: bool
    affects_system: bool
            decision = Decision.ALLOW

            level = RiskLevel.SAFE

        else:
    external_communication: bool


@dataclass
class RiskAssessment:

    level: RiskLevel
    score: float
    reasons: List[str]
    decision: Decision



            level = RiskLevel.LOW
class SafetyEngine:

        elif score >= 10:

    def assess(
        self,
        action: Action
    ) -> RiskAssessment:

        score = 0.0
        reasons = []

        if action.affects_data:


            level = RiskLevel.MEDIUM
            decision = Decision.CONFIRM
            score += 25

            decision = Decision.CONFIRM

        elif score >= 30:
            reasons.append(

            level = RiskLevel.HIGH
                "Action affects user data"
            )


        elif score >= 55:
        if action.affects_system:

            score += 30

            level = RiskLevel.CRITICAL
            decision = Decision.DENY

                "Action cannot easily be reversed"
            )

        if score >= 80:
            reasons.append(
                "Action affects system state"
            )

            reasons.append(

        if action.external_communication:


            score += 25
            score += 25

            reasons.append(
        if not action.reversible:

