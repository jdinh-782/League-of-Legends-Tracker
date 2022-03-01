import tkinter as tk
import tkinter.font
from PIL import Image, ImageTk, ImageDraw
from riotwatcher import LolWatcher
import urllib.request as u
from functools import partial
import pandas as pd
import json
import time
import numpy as np


summoner_name = input("Enter summoner name: ")

# grab summoner details
watcher = LolWatcher("YOUR_API_KEY")
summoner = watcher.summoner.by_name("na1", summoner_name)
print(f"\nsummoner characteristics: {summoner}")

# get latest patch version of league
latest_version = watcher.data_dragon.versions_for_region("na1")['n']['champion']
# print(latest_version)

# get summoner name and id
summoner_name = summoner['name']
# print(f"\n{summoner_name}'s id: {summoner['id']}")

# get summoner's ranked solo/flex stats
summoner_ranked = watcher.league.by_summoner('na1', summoner['id'])

# check to see if player has any ranked games in the past X days
if summoner_ranked:
    print(f"\nranked solo: {summoner_ranked[0]}")
    print(f"ranked solo tier: {summoner_ranked[0]['tier']}")
    print(f"ranked solo rank: {summoner_ranked[0]['rank']}")
    print(f"ranked solo W/L ratio: {summoner_ranked[0]['wins']} - {summoner_ranked[0]['losses']}")

    print(f"\nranked flex: {summoner_ranked[1]}")
    print(f"ranked flex tier: {summoner_ranked[1]['tier']}")
    print(f"ranked flex rank: {summoner_ranked[1]['rank']}")
    print(f"ranked flex W/L ratio: {summoner_ranked[1]['wins']} - {summoner_ranked[1]['losses']}")
else:
    print(f"\nno ranked games")

# get summoner's match history
summoner_matches = watcher.match.matchlist_by_account("na1", summoner['accountId'])
print(f"\n{summoner_name}'s matches: {summoner_matches['matches']}\n")

# get summoner's last match (or specific one)
match_index = 0
# print(f"\n{summoner_name}'s match {match_index}: {summoner_matches['matches'][match_index]}")

for i in range(0, 10):
    print(f"{summoner_name}'s match {i}: {summoner_matches['matches'][i]}")

while True:
    try:
        match_index = int(input("\nEnter a match index: "))

        if -1 < match_index < 9:
            break
        else:
            print("input must be in between 0 and 9")
    except ValueError:
        print("input must be an integer")

# get details of a summoner's match
match_details = watcher.match.by_id("na1", summoner_matches['matches'][match_index]['gameId'])
print(f"Details of {summoner_name}'s match: {match_details}")

match_type = match_details['gameMode']
print(f"game match type: {match_type}")

# add '0' to front if seconds is less than 10
s = '00'
if int(match_details['gameDuration'] % 60) < 10:
    s = f"0{int(match_details['gameDuration'] % 60)}"
match_duration = f"{int(match_details['gameDuration'] / 60)}:{s}"
print(f"game duration (in minutes : seconds): {match_duration}")

# convert given epoch time to human readable date
epoch = summoner_matches['matches'][match_index]['timestamp']  # originally given in milliseconds (convert to seconds)
match_date = time.strftime('%m/%d/%Y', time.gmtime(epoch / 1000))
print(f"game date: {match_date}\n")

# get the list of champions
champion_list = watcher.data_dragon.champions(latest_version, False, "en_US")
champion_dict = {}

for key in champion_list['data']:
    row = champion_list['data'][key]
    champion_dict[row['key']] = row['id']
# print(champion_dict)

participants = []
participant_summoner_names = []

for i in range(0, len(match_details['participantIdentities'])):
    participant_summoner_names.append(match_details['participantIdentities'][i]['player']['summonerName'])
    # print(participant_summoner_names[i])

# get item names using their id
items_json_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/item.json"
# print(items_json_url)
response = u.urlopen(items_json_url)
data_json = json.loads(response.read())

items = dict(data_json)['data']
# print(f"\ndictionary of items: {items}")

# get spell names using their 'key' value
spells_json_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
# print(f"\n{icon_url}")
response = u.urlopen(spells_json_url)
data_json = json.loads(response.read())

spells = dict(data_json)['data']
spells_dict = {}
# print(f"\ndictionary of spells: {spells}")
for key in spells:
    # print(spells[key])
    # print(spells[key]['name'], spells[key]['key'])
    # print(spells[key]['id'], spells[key]['key'])
    spells_dict[spells[key]['id']] = spells[key]['key']

keys_list = list(spells_dict.keys())
values_list = list(spells_dict.values())
# print(keys_list)
# print(values_list)

# create dataframe using match data
for row in match_details['participants']:
    # print(row)
    participants_row = {}
    participants_row['champion'] = champion_dict[str(row['championId'])]
    participants_row['win'] = row['stats']['win']
    participants_row['kills'] = row['stats']['kills']
    participants_row['deaths'] = row['stats']['deaths']
    participants_row['assists'] = row['stats']['assists']
    participants_row['spell 1'] = keys_list[values_list.index(str(row['spell1Id']))]
    participants_row['spell 2'] = keys_list[values_list.index(str(row['spell2Id']))]
    participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
    participants_row['goldEarned'] = row['stats']['goldEarned']
    participants_row['champLevel'] = row['stats']['champLevel']
    participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
    participants_row['item1'] = items[str(row['stats']['item0'])]['name'] if row['stats']['item0'] != 0 else 'None'
    participants_row['item2'] = items[str(row['stats']['item1'])]['name'] if row['stats']['item1'] != 0 else 'None'
    participants_row['item3'] = items[str(row['stats']['item2'])]['name'] if row['stats']['item2'] != 0 else 'None'
    participants_row['item4'] = items[str(row['stats']['item3'])]['name'] if row['stats']['item3'] != 0 else 'None'
    participants_row['item5'] = items[str(row['stats']['item4'])]['name'] if row['stats']['item4'] != 0 else 'None'
    participants_row['item6'] = items[str(row['stats']['item5'])]['name'] if row['stats']['item5'] != 0 else 'None'
    participants_row['item7'] = items[str(row['stats']['item6'])]['name'] if row['stats']['item6'] != 0 else 'None'
    participants_row['item1ID'] = row['stats']['item0']
    participants_row['item2ID'] = row['stats']['item1']
    participants_row['item3ID'] = row['stats']['item2']
    participants_row['item4ID'] = row['stats']['item3']
    participants_row['item5ID'] = row['stats']['item4']
    participants_row['item6ID'] = row['stats']['item5']
    participants_row['item7ID'] = row['stats']['item6']
    participants_row['W/L'] = 'L' if row['stats']['win'] is False else 'W'
    participants.append(participants_row)

df = pd.DataFrame(participants)
pd.set_option("display.max_columns", None)

df.insert(0, 'Summoner Names', participant_summoner_names)
print(df)

# get specific player's match details
index = int(df.index[df['Summoner Names'] == summoner_name].tolist()[0])
summoner_match_details = df.iloc[index]
print(f"\n{summoner_name}'s current match details\n{summoner_match_details}")

# get and save the summoner's profile icon
summoner_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/profileicon/" \
                    f"{str(summoner['profileIconId'])}.png"
# print(f"\n{summoner_name}'s profile icon: {summoner_icon_url}")
u.urlretrieve(summoner_icon_url, "summonerIcon.jpg")

# get and save the summoner's match champion icon
champion_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/" \
                    f"{summoner_match_details['champion']}.png"
# print(f"\n{summoner_name}'s match champion icon: {champion_icon_url}")
u.urlretrieve(champion_icon_url, "championIcon.png")

# # convert champion icon to a circular image
# # convert image to RGB and open as numpy array
# img = Image.open("summonerIcon.jpg").convert("RGB")
# np_image = np.array(img)
# h, w = img.size
#
# # create the same size alpha layer with a circle
# alpha = Image.new("L", [h, w], 0)
# draw = ImageDraw.Draw(alpha)
# draw.pieslice([0, 0, h, w], 0, 360, fill=255)
#
# # convert alpha image to numpy array
# np_alpha = np.array(alpha)
#
# # add alpha layer to RGB
# np_image = np.dstack((np_image, np_alpha))
#
# # save with alpha image
# Image.fromarray(np_image).save("sample.png")

# get and save the summoner's match spells icons
spell_1_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/spell/" \
                    f"{summoner_match_details['spell 1']}.png"
# print(f"\n{summoner_name}'s match spell 1 icon: {spell_1_icon_url}")
u.urlretrieve(spell_1_icon_url, "spell1Icon.png")

spell_2_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/spell/" \
                    f"{summoner_match_details['spell 2']}.png"
# print(f"\n{summoner_name}'s match spell 2 icon: {spell_2_icon_url}")
u.urlretrieve(spell_2_icon_url, "spell2Icon.png")

# get and save the summoner's match items' icons
# print(f"\n{summoner_name}'s match items' icons:\n")
for i in range(0, 7):
    s = f"item{i + 1}ID"
    item_id = summoner_match_details[s]
    item_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/{item_id}.png"
    # print(item_icon_url)

    if item_id != 0:
        u.urlretrieve(item_icon_url, f"item{i + 1}icon.png")
    else:
        u.urlretrieve("https://pbs.twimg.com/media/D-4YoRqWsAAd73n.jpg", f"item{i + 1}icon.png")


class MainWindow:
    def __init__(self, root):
        root.title("League of Legends Statistics Tracker")
        root.configure(background="#d9dadb")
        root.geometry("1440x900")

        # initialize top banner
        Banner()

        # initialize summonerIcon
        summoner_icon_image = ImageTk.PhotoImage(Image.open("summonerIcon.jpg").resize((100, 100)))
        summoner_icon_panel = tk.Label(root, image=summoner_icon_image, borderwidth=3, relief="solid", bg="white")
        summoner_icon_panel.place(x=25, y=125)

        # initialize summoner name and level
        text_font = tkinter.font.Font(family="Segoe UI", weight="bold")

        summoner_name_label = tk.Label(root, text=summoner_name)
        summoner_name_label.config(font=(text_font, 20))
        summoner_name_label.place(x=145, y=145)

        summoner_level_label = tk.Label(root, text=f"Level {summoner['summonerLevel']}")
        summoner_level_label.config(font=(text_font, 15))
        summoner_level_label.place(x=145, y=180)

        # initialize view type box (with buttons for each type)
        view_type_box = tk.Label(root, borderwidth=3, relief="solid", width=24, height=16, bg="#dee3de")
        view_type_box.place(x=25, y=250)

        self.view_type_buttons = list()
        view_types_list = ['Total', 'Ranked Solo', 'Ranked Flex', 'TFT', 'Statistics']
        view_types_y_coordinate = [270, 310, 350, 390, 430]

        for i in range(0, len(view_types_list)):
            viewTypeTextFont = tkinter.font.Font(family="Segoe UI", size=15)
            button = tk.Button(root, text=view_types_list[i], fg='black', font=viewTypeTextFont,
                               highlightthickness=0, bd=0, bg="#dee3de", activebackground="#dee3de")
            button.config(command=partial(self.clicked_button, button))

            self.view_type_buttons.append(button)

        for i in range(0, len(view_types_y_coordinate)):
            self.view_type_buttons[i].place(x=35, y=view_types_y_coordinate[i])

        # initialize display box
        display_box = tk.Label(root, borderwidth=3, relief="solid", width=169, height=41, bg="#dee3de")
        display_box.place(x=225, y=250)

        for counter in range(0, 1):
            # initialize match box with components
            match_box = self.create_match_box(root)
            match_box.place(x=325, y=275)

            match_type_label = tk.Label(root, text=match_type, bg="#dee3de")
            match_type_label.config(font=(text_font, 15))
            match_type_label.place(x=340, y=390)

            match_date_label = tk.Label(root, text=match_date, bg="#dee3de")
            match_date_label.config(font=(text_font, 15))
            match_date_label.place(x=780, y=390)

            kda = f"{summoner_match_details['kills']}/{summoner_match_details['deaths']}/{summoner_match_details['assists']}"
            kda_label = tk.Label(root, text=kda, bg="#dee3de")
            kda_label.config(font=(text_font, 15))
            kda_label.place(x=1225, y=390)

            win_or_lose = "VICTORY" if summoner_match_details['W/L'] == 'W' else "DEFEAT"
            win_or_lose_label = tk.Label(root, text=win_or_lose, bg="#dee3de")
            win_or_lose_label.config(font=(text_font, 15))
            win_or_lose_label.place(x=1205, y=300)

            match_duration_label = tk.Label(root, text=match_duration, bg="#dee3de")
            match_duration_label.config(font=(text_font, 15))
            match_duration_label.place(x=1244, y=325)

            item_icon_images = list()
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{1}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{2}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{3}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{4}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{5}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{6}icon.png").resize((50, 50))))
            item_icon_images.append(ImageTk.PhotoImage(Image.open(f"item{7}icon.png").resize((50, 50))))

            item_icons = list()
            for i in range(0, len(item_icon_images)):
                item_icon = tk.Label(root, image=item_icon_images[i], borderwidth=3, relief="solid", bg="black")
                item_icons.append(item_icon)

            item_icons_x_coordinate = [600, 665, 730, 795, 860, 925, 990]
            for i in range(0, len(item_icons)):
                item_icons[i].place(x=item_icons_x_coordinate[i], y=315)

            champion_icon_image = ImageTk.PhotoImage(Image.open("championIcon.png").resize((60, 60)))
            champion_icon_panel = tk.Label(root, image=champion_icon_image, borderwidth=3, relief="solid", bg="black")
            champion_icon_panel.place(x=340, y=300)

            spell_1_icon_image = ImageTk.PhotoImage(Image.open("spell1Icon.png").resize((25, 25)))
            spell_1_icon_panel = tk.Label(root, image=spell_1_icon_image, borderwidth=3, relief="solid", bg="black")
            spell_1_icon_panel.place(x=410, y=302)

            spell_2_icon_image = ImageTk.PhotoImage(Image.open("spell2Icon.png").resize((25, 25)))
            spell_2_icon_panel = tk.Label(root, image=spell_2_icon_image, borderwidth=3, relief="solid", bg="black")
            spell_2_icon_panel.place(x=410, y=333)

            if win_or_lose == "VICTORY":
                match_box.config(bg="#90c1f0")
                match_type_label.config(bg="#90c1f0")
                match_date_label.config(bg="#90c1f0")
                win_or_lose_label.config(bg="#90c1f0")
                match_duration_label.config(bg="#90c1f0")
                kda_label.config(bg="#90c1f0")
            else:
                match_box.config(bg="#ff7b7b")
                match_type_label.config(bg="#ff7b7b")
                match_date_label.config(bg="#ff7b7b")
                win_or_lose_label.config(bg="#ff7b7b")
                match_duration_label.config(bg="#ff7b7b")
                kda_label.config(bg="#ff7b7b")

        root.mainloop()

    # change button color when clicked and "disable" other buttons
    def clicked_button(self, button_type):
        if button_type['fg'] == "#6195b0":
            view_type_text_font = tkinter.font.Font(family="Segoe UI", size=15, weight="normal")
            button_type['fg'] = "black"
        else:
            for button in self.view_type_buttons:
                if button['text'] != button_type['text']:
                    button['fg'] = "black"
                    button['font'] = tkinter.font.Font(family="Segoe UI", size=15, weight="normal")

            view_type_text_font = tkinter.font.Font(family="Segoe UI", size=15, weight="bold")
            button_type['fg'] = "#6195b0"

        button_type['font'] = view_type_text_font

    def create_match_box(self,  root):
        return tk.Label(root, borderwidth=3, relief="solid", width=140, height=10, bg="#dee3de")


class Banner(tk.Frame):
    def __init__(self):
        super().__init__()
        self.create_banner()

    def create_banner(self):
        self.pack(fill="both", expand=1)

        canvas = tk.Canvas(self)
        canvas.create_rectangle(1920, 0, 0, 100, outline="#447fc7", fill="#447fc7")

        textFont = tkinter.font.Font(family="Segoe UI", size="35", weight="bold")
        # print(tk.font.families())

        canvas.create_text(720, 50, fill="white", font=textFont, text="League of Legends Statistics Tracker")
        canvas.pack(fill="both", expand=1)


window = tk.Tk()
t = MainWindow(window)
