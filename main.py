from collections import UserString
import tkinter as tk
from tkinter import ttk
import requests
import json
from PIL import Image, ImageTk
from io import BytesIO
import threading
import tkinter.messagebox as messagebox
import time
from plugins.init import func
func.proxies.scrape()
expected_assets = [
    {"id": 63690008, "name": "Pal Hair", "assetType": {"id": 41, "name": "HairAccessory"}, "currentVersionId": 8443736161},
    {"id": 86498048, "name": "Man Head", "assetType": {"id": 17, "name": "Head"}, "currentVersionId": 11008778043},
    {"id": 86500008, "name": "Man Torso", "assetType": {"id": 27, "name": "Torso"}, "currentVersionId": 11837972128},
    {"id": 86500036, "name": "Man Right Arm", "assetType": {"id": 28, "name": "RightArm"}, "currentVersionId": 11837973329},
    {"id": 86500054, "name": "Man Left Arm", "assetType": {"id": 29, "name": "LeftArm"}, "currentVersionId": 11837974431},
    {"id": 86500064, "name": "Man Left Leg", "assetType": {"id": 30, "name": "LeftLeg"}, "currentVersionId": 11837975410},
    {"id": 86500078, "name": "Man Right Leg", "assetType": {"id": 31, "name": "RightLeg"}, "currentVersionId": 11837976476},
    {"id": 144075659, "name": "Smile", "assetType": {"id": 18, "name": "Face"}, "currentVersionId": 339960860},
    {"id": 144076358, "name": "Blue and Black Motorcycle Shirt", "assetType": {"id": 11, "name": "Shirt"}, "currentVersionId": 339950145},
    {"id": 144076760, "name": "Dark Green Jeans", "assetType": {"id": 12, "name": "Pants"}, "currentVersionId": 339951177}
]

def ajouter_element():
    fichier = entry_nom.get()
    utilisateurs = lire_fichier_utilisateurs(fichier)

    thread = threading.Thread(target=tmain, args=(utilisateurs,))
    thread.start()

def tmain(utilisateurs):
    count = 0
    for utilisateur in utilisateurs:
        if count > 6:
            print('Pausing')
            func.proxies.scrape()
            time.sleep(20)
            count = 0
        thread = threading.Thread(target=recherche_utilisateurs_thread, args=(utilisateur,))
        thread.start()
        count += 1

def recherche_utilisateurs_thread(utilisateur):
    global expected_assets
    Name = utilisateur.split(":")[0].strip()
    pasw = utilisateur.split(":")[1].strip()
    User = CheckRobloxUser(Name)
    for config in User:
        id = config.get('UserId', '')
        r = get_user_avatar_items(id)
        print(r)
        rs = json.loads(r)
        if not all(item in rs["assets"] for item in expected_assets):
            titre = f"{config.get('Name', '')}"
            combo = titre + ':' + pasw
            description = config.get('HasVerifiedBadge', '')
            thumbnail_url = obtenir_thumbnail_url(id)
            thumbnail_image = telecharger_thumbnail(thumbnail_url)
            if thumbnail_image is not None:
                page_frame = ttk.Frame(canvas_frame)
                page_frame.pack(fill=tk.BOTH, padx=5, pady=5)

                thumbnail_label = ttk.Label(page_frame)
                thumbnail_label.image = thumbnail_image
                thumbnail_label.configure(image=thumbnail_image)
                thumbnail_label.pack(anchor=tk.W)

                titre_label = ttk.Label(page_frame, text=titre, font=("Helvetica", 12, "bold"), cursor="hand2")
                titre_label.pack(anchor=tk.W)
                titre_label.bind("<Button-1>", lambda event, combo=combo: copier_titre(event, combo))

                description_label = ttk.Label(page_frame, text=f"Description: {description}")
                description_label.pack(anchor=tk.W)


def get_user_avatar_items(user_id):
    url = f"https://avatar.roblox.com/v1/users/{user_id}/avatar"
    response = requests.get(url, proxies={"http": func.proxies.get()})
    return response.text


def lire_fichier_utilisateurs(fichier):
    try:
        with open(fichier, "r", encoding='utf-8') as f:
            lignes = f.readlines()
            return lignes
    except FileNotFoundError:
        print("The specified file can not be found.")
        messagebox.showerror("Error", "The specified file can not be found.")
    except Exception as e:
        print(f"An error occurred while reading the file : {e}")
        messagebox.showerror("Error", f"An error occurred while reading the file : {e}")

    return []


def obtenir_thumbnail_url(user_id):
    url_api_thumbnail = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=48x48&format=png"
    response = requests.get(url_api_thumbnail, proxies={"http": func.proxies.get()})
    data = json.loads(response.text)

    if "data" in data:
        user_data = data["data"]
        if user_data:
            thumbnail_url = user_data[0].get("imageUrl")
            return thumbnail_url

    return None


def telecharger_thumbnail(url):
    if url is None:
        return None

    response = requests.get(url, proxies={"http": func.proxies.get()})

    try:
        image = Image.open(BytesIO(response.content))
        thumbnail_image = ImageTk.PhotoImage(image)
        return thumbnail_image
    except (IOError, SyntaxError) as e:
        print(f"Error downloading image : {e}")

    return None


def CheckRobloxUser(nom):
    url = 'https://www.roblox.com/search/users/results?keyword=' + nom + '&maxRows=12&startIndex'
    response = requests.get(url, proxies={"http": func.proxies.get()})
    data = json.loads(response.text)

    utilisateurs = data.get("UserSearchResults", [])
    utilisateurs_trouves = []

    nom_lower = nom.lower()

    if len(utilisateurs) > 0:
        for utilisateur in utilisateurs:
            nom_utilisateur = utilisateur.get("Name", "").lower()
            noms_precedents = utilisateur.get("PreviousUserNamesCsv", "")
            noms_precedents_lower = [nom.lower().strip() for nom in noms_precedents.split(", ")]

            if nom_utilisateur == nom_lower or nom_lower in noms_precedents_lower:
                utilisateurs_trouves.append(utilisateur)
    else:
        print('unknown -> ' + nom)

    return utilisateurs_trouves

def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


def copier_titre(event, titre):
    root.clipboard_clear()
    root.clipboard_append(titre)
    messagebox.showinfo("Copy", "The combo has been copied")


root = tk.Tk()
root.title("RChecker - Roblox Combolist Viewer")
root.geometry("500x400")

frame = ttk.Frame(root)
frame.pack(pady=10)

scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

canvas_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=canvas_frame, anchor=tk.NW)

scrollbar.configure(command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

entry_nom = ttk.Entry(root)
entry_nom.pack(pady=5)

ajouter_button = ttk.Button(root, text="Add", command=ajouter_element)
ajouter_button.pack(pady=5)

canvas_frame.bind("<Configure>", on_canvas_configure)

root.mainloop()
