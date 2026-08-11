import os, requests, json, time
from dotenv import load_dotenv

load_dotenv()  # charge le .env situé dans le même dossier que le script

CLIENT_ID = os.environ["NETATMO_CLIENT_ID"]
CLIENT_SECRET = os.environ["NETATMO_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["NETATMO_REFRESH_TOKEN"]
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./")

def get_access_token():
    r = requests.post("https://api.netatmo.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_data():
    token = get_access_token()
    r = requests.get("https://api.netatmo.com/api/getstationsdata",
                      headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json()

def extract_module(module):
    dd = module.get("dashboard_data", {}) #dd pour dashboad_data
    return {
        "reachable": module.get("reachable", False), #reachable = accessible
        "temp": dd.get("Temperature"),
        "min_temp": dd.get("min_temp"),
        "date_min_temp": dd.get("date_min_temp"),
        "max_temp": dd.get("max_temp"),
        "date_max_temp": dd.get("date_max_temp"),
    }

def main():
    data = fetch_data()

    # Module principal
    module_principal = data["body"]["devices"][0]
    nom_principal = module_principal.get("module_name")

    result = {
        nom_principal: extract_module(module_principal),
    }

    for module in module_principal["modules"]:
        nom = module.get("module_name")
        result[nom] = extract_module(module)

    result["updated_at"] = int(time.time()) #Heure de l'exécution de ce programme (=génération du JSON)

    with open(os.path.join(OUTPUT_DIR, "meteo.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
