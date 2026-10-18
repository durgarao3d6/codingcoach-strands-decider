"""CodingCoach tools: concept library, challenge generator, and answer checker.

Synthetic data so the demo runs anywhere without external APIs.
Each tool has a clear one-line docstring — the model reads it.
"""

from __future__ import annotations

from strands import tool

# ---------------------------------------------------------------------------
# Concept library (synthetic, covers common beginner–intermediate topics)
# ---------------------------------------------------------------------------

_CONCEPTS: dict[str, dict] = {
    "recursion": {
        "definition": "A function that calls itself with a smaller input until a base case stops it.",
        "intuition": "Think of Russian nesting dolls: each doll contains a smaller one, until you reach the smallest.",
        "example": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)",
        "prerequisites": ["functions", "return values", "conditional statements"],
        "common_misconceptions": [
            "Forgetting the base case causes infinite recursion.",
            "Each call has its own local variables — they don't share state.",
            "Recursion is not always more efficient than a loop.",
        ],
    },
    "for loop": {
        "definition": "A control structure that repeats a block of code for each item in a sequence.",
        "intuition": "Like going through a to-do list and doing each task in order.",
        "example": "for item in ['a', 'b', 'c']:\n    print(item)",
        "prerequisites": ["variables", "lists"],
        "common_misconceptions": [
            "range(n) goes from 0 to n-1, not 1 to n.",
            "Modifying a list while iterating over it can skip items.",
        ],
    },
    "list comprehension": {
        "definition": "A compact way to build a list by applying an expression to each item in an iterable.",
        "intuition": "It's a for loop that builds a list, written in one line.",
        "example": "squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]",
        "prerequisites": ["for loop", "lists", "expressions"],
        "common_misconceptions": [
            "It creates a new list — it does not modify the original.",
            "The filter condition (if ...) goes at the end, not the beginning.",
        ],
    },
    "function": {
        "definition": "A named, reusable block of code that takes inputs (parameters) and returns an output.",
        "intuition": "Like a recipe: give it ingredients, get a dish back.",
        "example": "def add(a, b):\n    return a + b\n\nresult = add(3, 4)  # 7",
        "prerequisites": ["variables", "expressions"],
        "common_misconceptions": [
            "A function without 'return' returns None implicitly.",
            "Parameters are local — changes inside don't affect outside variables.",
        ],
    },
    "variable": {
        "definition": "A named container that stores a value in memory.",
        "intuition": "Like a labelled box: you put something in, use the label to get it back.",
        "example": "name = 'Alice'\nage = 30\nprint(name, age)",
        "prerequisites": [],
        "common_misconceptions": [
            "Variables in Python are references, not boxes — assigning a new value rebinds the name.",
            "Variable names are case-sensitive: 'Name' and 'name' are different.",
        ],
    },
    "dictionary": {
        "definition": "A collection of key-value pairs where each key maps to a value.",
        "intuition": "Like a real dictionary: look up a word (key) to get its definition (value).",
        "example": "person = {'name': 'Alice', 'age': 30}\nprint(person['name'])  # Alice",
        "prerequisites": ["variables", "lists"],
        "common_misconceptions": [
            "Keys must be immutable (strings, numbers, tuples) — lists cannot be keys.",
            "Accessing a missing key raises KeyError; use .get() for a safe default.",
        ],
    },
}

_FALLBACK_CONCEPT = {
    "definition": "This concept isn't in my library yet, but I'll do my best.",
    "intuition": "Think about what the name suggests.",
    "example": "# Try writing a small example yourself first.",
    "prerequisites": [],
    "common_misconceptions": [],
}


@tool
def get_concept(concept: str, programming_language: str = "Python", learner_level: str = "beginner") -> dict:
    """Retrieve a structured explanation of a programming concept: definition, intuition, example, prerequisites and common misconceptions."""
    key = concept.lower().strip()
    data = _CONCEPTS.get(key, _FALLBACK_CONCEPT)
    return {
        "concept": concept,
        "language": programming_language,
        "level": learner_level,
        **data,
    }


# ---------------------------------------------------------------------------
# Challenge bank
# ---------------------------------------------------------------------------

_CHALLENGES: dict[str, list[dict]] = {
    "recursion": [
        {
            "challenge_id": "rec-001",
            "title": "Countdown",
            "problem_statement": "Write a recursive function `countdown(n)` that prints n, n-1, ..., 1, 0.",
            "constraints": ["Must use recursion (no loops)", "n is a non-negative integer"],
            "examples": [{"input": "countdown(3)", "output": "3\n2\n1\n0"}],
            "hints": [
                "What is the smallest case where there is nothing left to do?",
                "After printing n, what should the next call receive?",
            ],
            "learning_objective": "base case + recursive step",
            "difficulty": "beginner",
        },
        {
            "challenge_id": "rec-002",
            "title": "Sum of a list",
            "problem_statement": "Write a recursive function `sum_list(lst)` that returns the sum of a list of numbers without using sum() or loops.",
            "constraints": ["Must use recursion", "Return 0 for an empty list"],
            "examples": [{"input": "sum_list([1, 2, 3, 4])", "output": "10"}],
            "hints": [
                "What is the sum of an empty list?",
                "How does the sum of [1,2,3,4] relate to 1 + sum_list([2,3,4])?",
            ],
            "learning_objective": "reduce a list recursively",
            "difficulty": "intermediate",
        },
    ],
    "for loop": [
        {
            "challenge_id": "loop-001",
            "title": "Print even numbers",
            "problem_statement": "Use a for loop to print every even number from 1 to 20 (inclusive).",
            "constraints": ["Use range()", "No list comprehensions"],
            "examples": [{"input": "(none)", "output": "2\n4\n6\n...\n20"}],
            "hints": ["range() can take a step argument.", "Alternatively, use an if statement inside the loop."],
            "learning_objective": "range() with step, or conditional inside loop",
            "difficulty": "beginner",
        }
    ],
    "list comprehension": [
        {
            "challenge_id": "lc-001",
            "title": "Squares of odds",
            "problem_statement": "Use a list comprehension to produce a list of squares of all odd numbers from 1 to 10.",
            "constraints": ["One line", "No for loops outside the comprehension"],
            "examples": [{"input": "(none)", "output": "[1, 9, 25, 49, 81]"}],
            "hints": [
                "A number is odd if n % 2 != 0.",
                "Put the filter condition after the for clause: [expr for x in ... if condition].",
            ],
            "learning_objective": "list comprehension with filter",
            "difficulty": "beginner",
        }
    ],
}

_FALLBACK_CHALLENGE = {
    "challenge_id": "gen-001",
    "title": "Write a small example",
    "problem_statement": "Write the smallest piece of code that demonstrates this concept working.",
    "constraints": ["Keep it under 10 lines"],
    "examples": [],
    "hints": ["Start with what you know.", "What is the simplest case that shows the idea?"],
    "learning_objective": "hands-on practice",
    "difficulty": "beginner",
}


@tool
def generate_challenge(
    concept: str,
    difficulty: str = "beginner",
    programming_language: str = "Python",
    learner_level: str = "beginner",
    known_misconceptions: str = "",
) -> dict:
    """Generate a coding exercise for a specific concept and difficulty level, with hints and a learning objective."""
    key = concept.lower().strip()
    pool = _CHALLENGES.get(key, [])
    # Pick by difficulty, fall back to first available, then generic
    match = next((c for c in pool if c["difficulty"] == difficulty), pool[0] if pool else None)
    result = dict(match or _FALLBACK_CHALLENGE)
    result["language"] = programming_language
    if known_misconceptions:
        result["note"] = f"Watch for these common mistakes: {known_misconceptions}"
    return result


# ---------------------------------------------------------------------------
# Answer checker
# ---------------------------------------------------------------------------

@tool
def check_answer(
    challenge_id: str,
    learner_answer: str,
    expected_behaviour: str = "",
    evaluation_rubric: str = "",
) -> dict:
    """Evaluate a learner's attempt against a challenge, identify misconceptions, and suggest the next step."""
    # Lightweight heuristic checks — no code execution (untrusted input safety)
    answer_lower = learner_answer.lower()

    # Check for common correct patterns per challenge
    checks: dict[str, dict] = {
        "rec-001": {
            "correct_signals": ["def countdown", "countdown(n-1)", "countdown(n - 1)", "if n", "return"],
            "misconception": "missing base case" if "if n" not in answer_lower else None,
        },
        "rec-002": {
            "correct_signals": ["def sum_list", "sum_list(lst[1:])", "lst[0]", "if not lst", "if len(lst)"],
            "misconception": "not slicing the list for the recursive call" if "lst[1:]" not in answer_lower else None,
        },
        "loop-001": {
            "correct_signals": ["for", "range", "print"],
            "misconception": None,
        },
        "lc-001": {
            "correct_signals": ["[", "for", "if", "**2", "* x" ],
            "misconception": "filter condition missing" if "if" not in answer_lower else None,
        },
    }

    rubric = checks.get(challenge_id)
    if rubric is None:
        # Generic evaluation for unknown challenge ids
        is_correct = len(learner_answer.strip()) > 10
        return {
            "is_correct": is_correct,
            "feedback": "I can see you've written something — let's talk through it together. Walk me through what your code does step by step.",
            "identified_misconception": None,
            "next_hint": "Explain your reasoning out loud (or in text) — that often reveals the gap.",
            "suggested_action": "check_answer",
            "uncertain": True,
        }

    signals = rubric["correct_signals"]
    matched = sum(1 for s in signals if s in answer_lower)
    is_correct = matched >= len(signals) * 0.6

    misconception = rubric.get("misconception") if not is_correct else None

    if is_correct:
        feedback = "That looks correct. Your key parts are all there."
        next_hint = None
        suggested_action = "generate_challenge"
    else:
        feedback = f"You have {matched} of {len(signals)} key elements. Something is missing or slightly off."
        next_hint = f"Think about: {misconception or 'review the structure of your solution'}."
        suggested_action = "give_hint"

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "identified_misconception": misconception,
        "next_hint": next_hint,
        "suggested_action": suggested_action,
        "uncertain": False,
    }


TOOLS = [get_concept, generate_challenge, check_answer]
