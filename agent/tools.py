"""AI agent tools: calculator, datetime, web search, and unit conversion."""

import math
import json
from datetime import datetime, timezone
import re


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression and return the result."""
    allowed = re.compile(r"^[\d\s\+\-\*\/\(\)\.\^%,a-z_A-Z]+$")
    if not allowed.match(expression.strip()):
        return "Error: expression contains invalid characters."
    try:
        # Replace ^ with ** for exponentiation
        expr = expression.replace("^", "**")
        # Expose safe math builtins
        safe_env = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "pow": pow,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "floor": math.floor,
            "ceil": math.ceil,
        }
        result = eval(expr, safe_env)  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


def get_current_datetime(timezone_name: str = "UTC") -> str:
    """Return the current date and time (UTC)."""
    now = datetime.now(timezone.utc)
    return now.strftime("Current UTC date/time: %Y-%m-%d %H:%M:%S UTC")


def search_web(query: str) -> str:
    """Return a simulated web-search result for the query."""
    return (
        f"Search results for '{query}':\n"
        "This is a demo environment without live internet access. "
        "To enable real web search, integrate a search API such as Brave Search, "
        "SerpAPI, or Bing Web Search and replace this function's body."
    )


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a value between common units."""
    conversions = {
        # Length (base: meter)
        "m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001,
        "mile": 1609.344, "miles": 1609.344,
        "ft": 0.3048, "feet": 0.3048, "foot": 0.3048,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "yard": 0.9144, "yards": 0.9144,
        # Weight (base: kilogram)
        "kg": 1.0, "g": 0.001, "lb": 0.453592, "lbs": 0.453592,
        "pound": 0.453592, "pounds": 0.453592,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
    }

    fu = from_unit.lower().strip()
    tu = to_unit.lower().strip()

    # Temperature conversions
    temp_units = {"c", "celsius", "f", "fahrenheit", "k", "kelvin"}
    if fu in temp_units or tu in temp_units:
        return _convert_temperature(value, fu, tu)

    if fu not in conversions:
        return f"Unknown unit: {from_unit}"
    if tu not in conversions:
        return f"Unknown unit: {to_unit}"

    base_value = value * conversions[fu]
    result = base_value / conversions[tu]
    return f"{value} {from_unit} = {round(result, 6)} {to_unit}"


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    celsius_map = {
        "c": value,
        "celsius": value,
        "f": (value - 32) * 5 / 9,
        "fahrenheit": (value - 32) * 5 / 9,
        "k": value - 273.15,
        "kelvin": value - 273.15,
    }
    if from_unit not in celsius_map:
        return f"Unknown temperature unit: {from_unit}"

    celsius = celsius_map[from_unit]

    if to_unit in ("c", "celsius"):
        result = celsius
    elif to_unit in ("f", "fahrenheit"):
        result = celsius * 9 / 5 + 32
    elif to_unit in ("k", "kelvin"):
        result = celsius + 273.15
    else:
        return f"Unknown temperature unit: {to_unit}"

    return f"{value} {from_unit} = {round(result, 4)} {to_unit}"


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluate a mathematical expression. "
                "Supports +, -, *, /, **, %, parentheses, sqrt, pi, e, sin, cos, tan, log."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2 + 2' or 'sqrt(16)'.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time in UTC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone_name": {
                        "type": "string",
                        "description": "Timezone name (currently only UTC is supported).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_units",
            "description": "Convert a value from one unit to another (length, weight, temperature).",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "The numeric value to convert.",
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "The source unit (e.g. 'km', 'kg', 'celsius').",
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "The target unit (e.g. 'miles', 'lbs', 'fahrenheit').",
                    },
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
]

# Map function names to callables
TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_current_datetime": get_current_datetime,
    "search_web": search_web,
    "convert_units": convert_units,
}
