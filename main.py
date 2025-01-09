import os
import requests
import time
import threading
import sys
from collections import deque
from bs4 import BeautifulSoup

queue = deque()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "authority": "anime3rb.com",
    "referrer": "https://anime3rb.com",
    "origin": "https://anime3rb.com", 
}

def download_video(url, filename):
    # Send a GET request to the URL
    response = requests.get(url, headers = headers, stream=True)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to download video: {response.status_code}")
        return

    # Get the total size of the video
    total_size = int(response.headers.get('content-length', 0))

    # Open the file in binary write mode
    os.makedirs(f"output", exist_ok=True)
    with open(f"output/{filename}", 'wb') as f:
        # Iterate over the response content in chunks
        for chunk in response.iter_content(chunk_size=1024):
            # Write the chunk to the file
            f.write(chunk)

            # Print the progress
            print(f"Downloading... {f.tell() / total_size * 100:.2f}%" + 50*' ', end = '\r')

def start_downloads(anime_name: str, episodes: int) -> None:
    while not queue:
        time.sleep(1)
    for counter in range(start, episodes + 1):
        link = queue.popleft()
        print(f"starting the download for episode {counter} out of {episodes} please wait...", end = '\r')
        ep_name = f"{anime_name} - episode {counter}-{episodes}"
        if counter == episodes:
            ep_name += " [END]"
        ep_name += '.mp4'
        
        download_video(link, ep_name)
        print(f"episode {counter}-{episodes} downloaded successfully")

def get_episode_cnt(soup: BeautifulSoup) -> int:
    cnt = soup.find_all('p', class_ = "text-lg leading-relaxed")[1]
    return int(cnt.text)

def get_episode_links(url: str, episodes: int) -> list[str]:
    res = []
    i = url.index("titles")
    base_url = url[:i] + "episode" + url[i + 6:]
    for episode in range(1, episodes + 1):
        res.append(base_url + '/' + str(episode))
    return res

def get_download_links(episode_links: list[str]) -> list[str]:
    global queue, start
    for episode in episode_links[start - 1:]:
        page = requests.get(episode, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        download_links_holder = soup.find("div", class_ = "flex-grow flex flex-wrap gap-4 justify-center")
        download_links = download_links_holder.find_all("label")
        desired = [1e9]
        for link in download_links:
            if "1080" in link.text:
                desired = [1080, link]
            elif "720" in link.text:
                if desired[0] == 1080:
                    desired = [720, link]
            else:
                desired = [480, link]
        queue.append(desired[1].parent["href"])
    return

def main(url) -> None:
    # GREETINGS
    MY_NAME = """
██   ██ ███████ ██      ███    ███ ██    ██ 
██   ██ ██      ██      ████  ████  ██  ██  
███████ █████   ██      ██ ████ ██   ████   
██   ██ ██      ██      ██  ██  ██    ██    
██   ██ ███████ ███████ ██      ██    ██    
"""
    print(MY_NAME)
    print("Welcome to Anime3rb Downloader")

    # get the anime page's url
    # url = input("Enter the url of the anime (e.g. https://anime3rb.com/titles/naruto): ")
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")

    anime_name = url[url.index("titles") + 7:]

    # get the number of episodes
    episodes_cnt = get_episode_cnt(soup)

    # get the episode links
    episode_links = get_episode_links(url, episodes_cnt)

    global start
    # start = int(input("Enter the episode to start downloading from: "))
    start = 1
    while start < 1 or start > episodes_cnt:
        start = int(input("Please enter a valid number: "))

    # start the thread to collect the download links
    threading.Thread(target = get_download_links, args = [episode_links]).start()

    # start downloading from the queue made by the thread
    start_downloads(anime_name, episodes_cnt)

    # end the programm with a pause and a thanks message ^_^
    print("Thanks for using Anime3rb Downloader :)")
    print("Press any key to exit...")
    os.system("pause > nul")
    os.system("exit")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        main(input("Enter the url of the anime (e.g. https://anime3rb.com/titles/naruto): ").strip())
    else: 
        main(sys.argv[1])