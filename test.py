
import requests 
import bs4

r = requests.get("https://dev.bukkit.org/projects/orebfuscator-anti-x-ray")
soup = bs4.BeautifulSoup(r.text)

before = soup.find("div", string="Total Downloads")
print(before.find_next("div").string.replace(",", ""))