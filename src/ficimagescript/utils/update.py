import httpx
from packaging.version import parse


def check_for_update(current_version: str):
    """Checks if a new version of FicImage is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/FicImageScript/json"
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]

        if parse(latest_version) > parse(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print("Run `pip install --upgrade FicImageScript` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")
            print("♥ Enjoying FicImage? Check out `ficimage --credits`")

    except httpx.RequestError as e:
        print(f"Unable to check for updates: {e}")


def show_credits():
    print("\nFicImage - Made by @Jemeni11")
    print("\nWhy I built this:")
    print("""
    ℹ️  NOTE: FicHub is a growing set of accessibility tools for reading fanfiction.

    FicHub (https://fichub.net/) is great - it really is. But after one too many times of copying
    image links to open in my browser, I had to find an alternative. Building this tool wasn't my
    first thought. I initially found leech.py (https://github.com/kemayo/leech), but its image
    support was still a work in progress.

    After discovering a PR (https://github.com/kemayo/leech/pull/84) that added basic image support,
    I expanded on that code, which eventually became the core of what we now call FicImage.

    The project wouldn't be where it is today without Iris (FicHub's creator), who helped with the
    finishing touches by fixing a major bug that prevented v1 from working properly. She also
    suggested making it a proper package which was something I hadn't even considered at the time.

    So thank you to Iris for both creating FicHub and helping with this project. Without FicHub,
    this tool obviously wouldn't exist (lol).

    Check out FicHub:
    ✦  Website (https://fichub.net/)
    ✦  GitHub (https://github.com/FicHub/fichub.net)
    ✦  Discord (https://discord.gg/sByBAhX)

    I've also made other Fanfiction tools like FicRadar (https://github.com/Jemeni11/FicRadar/),
    TalesTrove (https://github.com/Jemeni11/TalesTrove) and contributed to
    WebToEpub (https://github.com/dteviot/WebToEpub) and Leech.py (https://github.com/kemayo/leech).

    Thank you
    """)

    print("\nFind me at:")
    print("  ✦  GitHub: https://github.com/Jemeni11")
    print("  ✦  GitLab: https://gitlab.com/Jemeni11")
    print("  ✦  LinkedIn: https://linkedin.com/in/emmanuel-jemeni")
    print("  ✦  BlueSky: https://bsky.app/profile/jemeni11.bsky.social")
    print("  ✦  Twitter/X: https://twitter.com/Jemeni11_")
    print("\nSupport FicImage:")
