from concurrent.futures import ThreadPoolExecutor

import requests

csrftoken = "ieC7FVwc5aIwOHP8jxHVoltopmYR0KfL"


def post_command(action: str):
    return requests.post(
        "http://localhost:4205/api/command/",
        data={"action": action, "a": 1},
        cookies={"csrftoken": csrftoken},
        headers={
            "X-CSRFToken": csrftoken,
            "Referer": "http://localhost:4205/",
        },
    )


def run_requests_in_parallel():
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(post_command, "test")
        future2 = executor.submit(post_command, "test")
        resp1 = future1.result()
        resp2 = future2.result()
        print(resp1.status_code, resp1.text)
        print(resp2.status_code)


run_requests_in_parallel()
