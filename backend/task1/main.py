
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def parse_handwriting(recipient_name: str) -> str:
    """
    Parse the handwriting of the recipient's name
    and return the name in a readable format.

    Args:
    recipient_name (str): The recipient's name in handwriting.

    Returns:
    str: The recipient's name in a readable format.
    """
    if not recipient_name:
        return ""

    # Clean up the recipient name
    recipient_name = re.sub(r'[_-]+', ' ', recipient_name)
    recipient_name = re.sub(r'[^a-zA-Z\s]','',recipient_name)
    recipient_name = re.sub(r'\s+', ' ', recipient_name).strip()

    recipient_name =  re.sub(r'\b\w', lambda match: match.group(0).upper(), recipient_name.lower())

    if len(recipient_name.split()) <= 0:
        return None
    return recipient_name


@app.route("/parse", methods=["POST"])
def parse():
    data = request.get_json()
    if "input" not in data or not isinstance(data["input"], str):
        return jsonify({"error": "Invalid input"}), 400

    cleaned_text = parse_handwriting(data["input"])
    if not cleaned_text:
        return jsonify({"error": "Invalid input"}), 400

    return jsonify({"msg": cleaned_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)