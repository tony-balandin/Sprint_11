from uuid import uuid4


def generate_unique_email() -> str:
    return f"qa_desk_{uuid4().hex[:12]}@example.com"
