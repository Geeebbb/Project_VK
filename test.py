import requests
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000"
def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        pprint(response.json())
    except:
        print(f"Response content: {response.text}")
    print("-" * 50)


def test_all_segments():

    print("\n1. Создаем 100 тестовых пользователей:")
    for user_id in range(15230, 15330):
        response = requests.post(
            f"{BASE_URL}/users/",
            json={"id": user_id}
        )
        print(f"User {user_id}: {response.status_code}")

    print("\n2. Создаем все сегменты:")
    segments = ["MAIL_VOICE_MESSAGES", "CLOUD_DISCOUNT_30", "MAIL_GPT"]
    for segment in segments:
        response = requests.post(
            f"{BASE_URL}/segments/",
            json={"name": segment}
        )
        print_response(response)

    print("\n3. Добавляем сегменты конкретным пользователям:")
    test_cases = [
        {"user_id": 15230, "segments": ["MAIL_VOICE_MESSAGES", "CLOUD_DISCOUNT_30", "MAIL_GPT"]},
        {"user_id": 15231, "segments": ["MAIL_GPT"]},
        {"user_id": 15232, "segments": ["CLOUD_DISCOUNT_30"]}
    ]

    for case in test_cases:
        for segment in case["segments"]:
            response = requests.post(
                f"{BASE_URL}/users/add_segment/",
                json={"user_id": case["user_id"], "segment_name": segment}
            )
        print(f"User {case['user_id']} segments: {case['segments']}")
        print_response(response)



    print("\n4. Распределяем MAIL_GPT на 30% пользователей:")
    response = requests.post(
        f"{BASE_URL}/segments/distribute/",
        json={"segment_name": "MAIL_GPT", "percent": 30.0}
    )
    print_response(response)

    print("\n5. Распределяем MAIL_VOICE_MESSAGES на 50% пользователей:")
    response = requests.post(
        f"{BASE_URL}/segments/distribute/",
        json={"segment_name": "MAIL_VOICE_MESSAGES", "percent": 50.0}
    )
    print_response(response)

    print("\n6. Распределяем CLOUD_DISCOUNT_30 на 70% пользователей:")
    response = requests.post(
        f"{BASE_URL}/segments/distribute/",
        json={"segment_name": "CLOUD_DISCOUNT_30", "percent": 70.0}
    )
    print_response(response)

    print("\n7. Проверяем сегменты пользователей:")
    for user_id in range(15230, 15330):
        response = requests.get(f"{BASE_URL}/users/{user_id}/segments/")
        print(f"User {user_id} segments:", end=" ")
        print_response(response)


if __name__ == "__main__":
    test_all_segments()