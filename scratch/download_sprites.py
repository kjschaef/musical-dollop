import urllib.request
import os

base_dir = "assets/characters"
os.makedirs(base_dir, exist_ok=True)

# We will use some pixel art sprites available on raw github content or wikimedia
# Since direct links might be hard to guess, let's download some known free assets
sprites = {
    "enemy.png": "https://raw.githubusercontent.com/komefai/zelda-sprites/master/enemies/octorok_red.png",
    "troll.png": "https://raw.githubusercontent.com/komefai/zelda-sprites/master/enemies/moblin_blue.png",
    "snake.png": "https://raw.githubusercontent.com/komefai/zelda-sprites/master/enemies/rope.png",
    "dragon.png": "https://raw.githubusercontent.com/komefai/zelda-sprites/master/bosses/aquamentus.png"
}

for name, url in sprites.items():
    filepath = os.path.join(base_dir, name)
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded {name} successfully.")
    except Exception as e:
        print(f"Failed to download {name} from {url}: {e}")

