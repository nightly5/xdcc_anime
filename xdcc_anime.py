#!/usr/bin/python3

"""
Script to list all the packlists to download for a given anime.

Used to be used in [Ritsu bot](https://github.com/supershadoe/ritsu)
but removed as the usage would be very low.
Also to be less in the gray area legally.
"""

__author__ = "nightly5"
__license__ = "MIT"


from collections import OrderedDict
import re
import typing as t

import requests


BOTS: OrderedDict[str, str] = OrderedDict({
    "CR-HOLLAND|NEW": "https://arutha.info/xdcc/CR-NL.NEW.xdcc.txt",
    "CR-ARUTHA|NEW": "https://arutha.info/xdcc/CR-ARUTHA.NEW.xdcc.txt",
})
"""Mapping of all bots to their packlists"""

PRINT_EACH_PACK: bool = False

for _res in ('720', '1080'):
    BOTS[f"ARUTHA-BATCH|{_res}p"] = f"https://arutha.info/xdcc/ARUTHA-BATCH.{_res}p.xdcc.txt"
del _res


class Episode(t.TypedDict):
    """
    t.TypedDict for describing the match groupdict returned by re engine.

    Each key corresponds to a named match group.
    """
    PackNum: str
    FileSize: str
    Uploader: str
    AnimeName: str
    EpisodeNo: str


def main() -> None:
    """
    The main function that's run when the script is not imported from elsewhere.
    """
    anime_name: str = input("Enter the name of the anime: ")
    if not anime_name:
        print(
            "\033[36mAre you practising air-typing?\n"
            "\033[1;31mType an anime name.\033[0m"
        )
        exit(1)
    anime_name = re.escape(anime_name)

    res: str = input(
        "Enter the resolution for download (480p/720p/1080p): ").casefold()
    if not re.search(r"(\d+)p", res):
        print(f"\033[1;31m{res} is not a valid resolution.\033[0m")
        exit(1)

    print("List of bots available: ")
    for i, bot in enumerate(BOTS, 1):
        print(
            f"    \033[1m{i if len(BOTS) > 1 else ''}.\033[0;36m {bot}\033[0m"
        )
    bot: str = input(
        "Enter the number or the name of bot(case-sensitive): "
    )
    try:
        if (i := int(bot) - 1) < 0:
            print("\033[1;31mThere is no bot for the given number.\033[0m")
            exit(1)
        bot = tuple(BOTS.items())[i][0]
    except IndexError:
        print("\033[1;31mThere is no bot for the given number.\033[m")
        exit(1)
    except ValueError:
        if bot not in BOTS:
            print("\033[1;31mThere is no such bot.\033[m")
            exit(1)

    fetch_data(anime_name, res, bot)


def fetch_data(anime_name: str, res: str, bot: str) -> None:
    """
    Fetches the data using a requests session.
    """
    with requests.session() as session:
        print("\033[36mFetching data from the bot…\033[0m")
        try:
            with session.get(BOTS[bot]) as r:
                if r.status_code == 200:
                    process_data(anime_name, res, bot, r.text)
                else:
                    print(
                        "\033[31mThe required data cannot be fetched."
                        f" \033[1;36m{r.status_code} {r.reason}\033[0m"
                    )
        except KeyboardInterrupt:
            print("\033[31mRequest manually stopped by the user.\033[0m")
            exit(130)


def process_data(anime_name: str, res: str, bot: str, text: str) -> None:
    """
    Process the text obtained from the bot and print the results.
    """
    def _extract_pack_info(
        pack_nums: list[str], names: list[str], data: t.Iterator[re.Match[str]]
    ) -> None:
        if PRINT_EACH_PACK:
            print("\033[32mPRINT_EACH_PACK is on, set this to False to avoid spam on terminal…\033[0m")
        for ep_match in data:
            episode = t.cast(Episode, ep_match.groupdict())
            pack_nums.append(episode["PackNum"])
            if (name := episode["AnimeName"]) not in names:
                names.append(name)
            if PRINT_EACH_PACK:
                print_result(episode)

    pack_nums: list[str] = []
    anime_names: list[str] = []
    data: t.Iterator[re.Match[str]] = deserialize_data(anime_name, res, text)

    _extract_pack_info(pack_nums, anime_names, data)
    if not pack_nums:
        data = deserialize_data(anime_name, res, text, False)
        _extract_pack_info(pack_nums, anime_names, data)

    print(
        f"\n\033[1;33m{len(pack_nums)}\033[0m entries matched "
        f"and \033[1;33m{len(anime_names)}\033[0m unique titles found."
    )
    print("\033[1mUnique titles found:\033[0m")
    for i, name in enumerate(anime_names, 1):
        print(
            f"    \033[1m{i if len(anime_names) > 1 else ''}. "
            f"\033[0;36m{name}\033[0m"
        )
    filter: str = input(
        "Do you want to change the search term? "
        "If yes, enter the new search term: "
    )
    if filter:
        print()
        process_data(re.escape(filter), res, bot, text)
        return

    if not pack_nums:
        print(
            "\033[1;31mNo matches were found. "
            "Check the spelling, bot and resolution chosen.\033[0m"
        )
    else:
        print(
            "\n\033[1mTo download the latest episode, use "
            f"\033[33m/msg {bot} xdcc send {pack_nums[-1]}"
            "\033[0m"
        )
        comb_pack_nums: list[list[str] | str] = [pack_nums[0]]
        for pack in pack_nums[1:]:
            temp: list[str] | str = comb_pack_nums.pop()
            if (
                isinstance(temp, str)
                and int(pack[1:]) - int(temp[1:]) == 1
            ):
                comb_pack_nums.append([temp, pack])
            elif (
                isinstance(temp, list)
                and int(pack[1:]) - int(temp[1][1:]) == 1
            ):
                temp[1] = pack
                comb_pack_nums.append(temp)
            else:
                comb_pack_nums.extend((temp, pack))
        pack_nums = [
            e if isinstance(e, str) else '-'.join(e)
            for e in comb_pack_nums
        ]
        print(
            "\n\033[1mTo download in batch, use "
            f"\033[33m/msg {bot} xdcc batch {','.join(pack_nums)}"
            "\033[0m"
        )


def deserialize_data(
    anime: str, res: str, data: str, subsplease: bool = True
) -> t.Iterator[re.Match[str]]:
    """
    Provides an iterative interface to the fetched data using Python's regex
    engine which returns a match object on each iteration.
    """
    re_text: str = (
        r"(?P<PackNum>#\d+)(?:\s*)"
        r"(?:[\dx]+)(?:[\s\[]+)"
        r"(?P<FileSize>[\d\.BKMGT]+)(?:[\]\s\[]+)"
        r"(?P<Uploader>.+)(?:\])(?:\s*)"
        fr"(?P<AnimeName>{anime}.*)(?:\s-\s)"
        fr"(?P<EpisodeNo>[v\d]+)(?:[\s]*"
    )
    if subsplease:
        return re.finditer(fr"{re_text}\({res})", data, flags=re.IGNORECASE)
    else:
        return re.finditer(fr"{re_text}\[{res})", data, flags=re.IGNORECASE)


def print_result(episode: Episode) -> None:
    """
    Prints result in packlist format (but filtered and easy-to-digest).
    """
    print(
        f"\033[32m{episode['PackNum']} \033[35m{episode['AnimeName']} \033[0m- "
        f"\033[36m{episode['EpisodeNo']} \033[0;1m({episode['FileSize']})"
        f"\033[0m by {episode['Uploader']}"
    )


if __name__ == "__main__":
    main()
