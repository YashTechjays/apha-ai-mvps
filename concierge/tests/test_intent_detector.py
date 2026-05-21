from backend.ai.intent_detector import detect_intent


def test_join_intent():
    assert detect_intent("I want to join APhA") == "join"
    assert detect_intent("How do I sign up for membership?") == "join"


def test_renew_intent():
    assert detect_intent("My membership expired, how do I renew?") == "renew"


def test_cpe_intent():
    assert detect_intent("How many CPE hours do I get with membership?") == "cpe"


def test_pricing_intent():
    assert detect_intent("How much does membership cost?") == "pricing"


def test_off_topic_intent():
    assert detect_intent("What's the weather like today?") == "off_topic"


def test_general_question():
    assert detect_intent("Tell me about APhA") == "question"
