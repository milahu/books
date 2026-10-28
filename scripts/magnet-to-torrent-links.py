#!/usr/bin/env python3

# workaround for: github is censoring magnet links

# https://stackoverflow.com/questions/60596615
# How to make torrent magnet url clickable in Markdown?


import os
import re
import json
import shutil
import urllib.parse


def main():

    # ~/.config/cas.json
    r'''
    {
      "dirs": [
        "/mnt/sdb/cas"
      ]
    }
    '''
    with open(os.path.expanduser("~/.config/cas.json")) as f:
        cas_config = json.load(f)
    print(f"cas_config: {cas_config}")

    cas_dirs = cas_config["dirs"]
    print(f"cas_dirs: {cas_dirs!r}")

    os.makedirs("cas/btih", exist_ok=True)

    with open("readme.md") as f:
        md = f.read()

    regex = r"\[(.*?)\]\((magnet:.*?)\)"

    def replace(match):
        name, url = match.groups()
        xt = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["xt"][0]
        assert xt.lower().startswith("urn:btih:"), f"bad xt: {xt}"
        btih = xt.split(":")[2].lower()
        torrent_src = None
        for cas_dir in cas_dirs:
            torrent_src = f"{cas_dir}/btih/{btih}.torrent"
            if os.path.exists(torrent_src):
                break
            else:
                torrent_src = None
        if torrent_src is None:
            print(f"error: missing torrent file: {btih}.torrent")
            # dont replace the magnet link
            return match.group(0)
        torrent = f"cas/btih/{btih}.torrent"
        shutil.copy(torrent_src, torrent)
        replacement = f"[{name}]({torrent})"
        print(f"replacement: {replacement}")
        return replacement

    md = re.sub(regex, replace, md)

    with open("readme.md", "w") as f:
        f.write(md)


if __name__ == "__main__":
    main()
