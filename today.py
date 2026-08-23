import os
import requests


USERNAME = "batualkoc"
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def get_user():
    url = f"https://api.github.com/users/{USERNAME}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def get_repositories():
    repositories = []

    page = 1

    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos"

        params = {
            "per_page": 100,
            "page": page,
            "type": "owner"
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def calculate_stats():
    user = get_user()
    repos = get_repositories()

    repository_count = len(
        [
            repo
            for repo in repos
            if not repo["fork"]
        ]
    )

    stars = sum(
        repo["stargazers_count"]
        for repo in repos
        if not repo["fork"]
    )

    followers = user["followers"]

    return {
        "REPOS": repository_count,
        "FOLLOWERS": followers,
        "STARS": stars
    }


def update_svg(filename, stats):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()

    # Daha önce sayı yazılmışsa template'i yeniden üretmek
    # yerine mevcut placeholder'ları değiştiriyoruz.
    for key, value in stats.items():
        placeholder = "{{" + key + "}}"

        if placeholder in content:
            content = content.replace(
                placeholder,
                str(value)
            )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def main():
    stats = calculate_stats()

    print("GitHub statistics:")
    print(stats)

    update_svg(
        "dark_mode.svg",
        stats
    )

    update_svg(
        "light_mode.svg",
        stats
    )


if __name__ == "__main__":
    main()
