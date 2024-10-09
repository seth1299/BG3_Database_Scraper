import requests
from bs4 import BeautifulSoup
import sqlite3

# URL for the "List of Weapons" page
url = 'https://bg3.wiki/wiki/List_of_weapons'

# Connect to SQLite database (or create it)
conn = sqlite3.connect('bg3_weapons.db')
cursor = conn.cursor()

# Create weapons table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS weapons (
                    name TEXT, 
                    enchantment TEXT, 
                    damage TEXT, 
                    damage_type TEXT, 
                    weight REAL, 
                    price INTEGER, 
                    special TEXT
                )''')

# Function to strip unnecessary characters from enchantments
def strip_enchantment(enchant):
    return enchant.replace('+', '').strip()

# Function to convert weight into kg (assumes kg format is always given)
def convert_weight(weight_text):
    weight = weight_text.split(' ')[0]
    return float(weight)

# Scraping function
def scrape_weapons():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Target tables based on the sections you care about
    sections = ["Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
    for section in sections:
        section_header = soup.find('span', id=section)
        if section_header:
            table = section_header.find_next('table', class_='wikitable sortable bg3wiki-weapons-table')
            rows = table.find_all('tr')[1:]  # Skip the header row

            for row in rows:
                cells = row.find_all('td')
                valid_dice = ["d4", "d6", "d8", "d10", "d12"]

                if len(cells) < 7:  # Ensure correct row structure
                    continue

                # Parse each column
                name = cells[0].get_text(strip=True)
                enchantment = strip_enchantment(cells[1].get_text(strip=True))
                #print("RAWR ", cells[2].get_text())
                #if ( "<br>" in cells[2].get_text() ):
                    #damage = "This one has a line break"
                #else:
                damage = cells[2].get_text(strip=True)
                damage_type = cells[3].get_text(strip=True)
                weight = convert_weight(cells[4].get_text(strip=True))
                price = cells[5].get_text(strip=True)
                special = cells[6].get_text(strip=True)
                
                if len(damage) > 3:
                    for die in valid_dice:
                        numberOfDice = damage.count(die)
                        while numberOfDice > 1:
                            i = damage.index(die)
                            tempString = damage[0] + die + ", " + damage[0] + die
                            #tempString = tempString[tempString.index(", "):]
                            damage = tempString
                            numberOfDice -= 1

                for character in damage_type:
                    if character.isupper():
                        characterIndex = damage_type.index(character)
                        damage_type = damage_type[0:characterIndex] + ", " + damage_type[characterIndex:]
                        
                
                item = [name, enchantment, damage, damage_type, weight, price, special]
                print(item)

                # Exclude items "Not usable by humanoids"
                if "Not usable by humanoids" in special:
                    continue

                # Insert into the SQLite database
                cursor.execute('''INSERT INTO weapons (name, enchantment, damage, damage_type, weight, price, special) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (name, enchantment, damage, damage_type, weight, price, special))

    # Commit changes and close connection
    conn.commit()

scrape_weapons()
conn.close()
