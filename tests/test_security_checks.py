import ast
import os


def get_field_names(filepath: str) -> list[str]:
    with open(filepath) as f:
        tree = ast.parse(f.read())
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if not isinstance(item, ast.AnnAssign):
                    continue
                if isinstance(item.target, ast.Name):
                    names.append(item.target.id)
    return names


def test_card_number_not_in_any_model():
    for root, _, files in os.walk("modules"):
        for file in files:
            if file == "model.py":
                fields = get_field_names(os.path.join(root, file))
                assert "card_number" not in fields, (
                    f"card_number found in {root}/{file}"
                )


def test_card_number_not_in_any_response_schema():
    for root, _, files in os.walk("modules"):
        for file in files:
            if file != "schema.py":
                continue
            filepath = os.path.join(root, file)
            with open(filepath) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                is_response = (
                    isinstance(node, ast.ClassDef)
                    and "Response" in node.name
                )
                if not is_response:
                    continue
                for item in node.body:
                    if not isinstance(item, ast.AnnAssign):
                        continue
                    if isinstance(item.target, ast.Name):
                        assert item.target.id != "card_number", (
                            f"card_number found in {node.name} in {filepath}"
                        )