# from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re
from pydantic import BaseModel, ValidationError, Field

# ==== Type Definitions, feel free to add or modify ===========================
class CookbookEntry(BaseModel):
    name: str
    type: str

class RequiredItem(BaseModel):
    name: str
    quantity: int = Field(..., gt=0)

class Recipe(CookbookEntry):
    type: str = "recipe"
    requiredItems: List[RequiredItem]

class Ingredient(CookbookEntry):
    type: str = "ingredient"
    cookTime: int = Field(..., ge=0)


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: Dict[str, Union[Recipe, Ingredient]] = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
    data = request.get_json()
    recipe_name = data.get('input', '')
    parsed_name = parse_handwriting(recipe_name)
    if parsed_name is None:
        return 'Invalid recipe name', 400
    return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that
def parse_handwriting(recipeName: str) -> Union[str | None]:
    """
    Parse the handwriting of the recipient's name
    and return the name in a readable format.

    Args:
    recipeName (str): The recipient's name in handwriting.

    Returns:
    str: The recipient's name in a readable format.
    """
    if not recipeName or recipeName.strip() == "":
        return None

    # Clean up the recipient name
    recipeName = re.sub(r'[^a-zA-Z\s]', '',
                re.sub(r'\s+', ' ',
                re.sub(r'[_-]+', ' ', recipeName))).strip().title()

    return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
    """
    Endpoint that adds an entry to the cookbook.
    """
    data = request.get_json()

    # Validate type
    if data.get("type") not in ["recipe", "ingredient"]:
        return jsonify({"error": "Invalid type. Must be 'recipe' or 'ingredient'"}), 400

    # Check if name already exists
    if data["name"] in cookbook:
        return jsonify({"error": "Name already exists"}), 400

    try:
        # Validate using Pydantic
        entry = Recipe(**data) if data["type"] == "recipe" else Ingredient(**data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Store valid entry
    cookbook[entry.name] = entry.model_dump()
    return jsonify({}), 200

# [TASK 3] ====================================================================
# Helper function to calculate total cooktime and ingredient quantities
def calculate_recipe_total(target: str):
    if target not in cookbook:
        raise ValueError(f"Recipe '{target}' not found")

    recipe = cookbook[target]

    # Base Case: If it's an ingredient, return cookTime and count
    if recipe["type"] == "ingredient":
        return recipe["cookTime"], {recipe["name"]: 1}

    # Recursive Case: If it's a recipe
    total_cook_time = 0
    ingredient_count = {}

    for item in recipe["requiredItems"]:
        cook_time, count = calculate_recipe_total(item["name"])  # Recursive call
        total_cook_time += cook_time * item["quantity"]  # Multiply cook time by quantity

        # Aggregate ingredient counts
        for ingredient, quantity in count.items():
            if ingredient in ingredient_count:
                ingredient_count[ingredient] += quantity * item["quantity"]
            else:
                ingredient_count[ingredient] = quantity * item["quantity"]

    return total_cook_time, ingredient_count


# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
    """
    Endpoint that returns a summary of a recipe given its name.
    """
    name = request.args.get('name')
    if name not in cookbook:
        return jsonify({"error": "Entry not found"}), 400

    entry = cookbook[name]

    # If the entry is an ingredient, return its details directly
    if entry["type"] == "ingredient":
        return jsonify(entry), 200

    # If the entry is a recipe, generate a summary
    total_cook_time, ingredient_count = calculate_recipe_total(name)
    summary = {
        "name": entry["name"],
        "totalCookTime": total_cook_time,
        "ingredients": [{"name": ing, "quantity": qty} for ing, qty in ingredient_count.items()]
    }

    return jsonify(summary), 200


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=8080)
