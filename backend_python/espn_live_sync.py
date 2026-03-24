import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import schedule
import time
from datetime import datetime

# ==========================================
# 1. FIREBASE AUTHENTICATION
# ==========================================
# Go to Firebase Console -> Project Settings -> Service Accounts
# Generate a new private key and save it as "serviceAccountKey.json" in this folder.
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com/'
    })
    print("✅ Successfully connected to Firebase Cloud Architecture.")
except Exception as e:
    print("⚠️ Firebase Authentication Error. Ensure 'serviceAccountKey.json' is present.")
    print("Error Details:", e)

# ==========================================
# 2. ESPN MULTI-SPORT POLLING LOGIC
# ==========================================
def fetch_and_sync_espn():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executing Global API Poll...")
    
    # Endpoints to poll
    endpoints = {
        "bkb": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
        "cfb": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
        "bsb": "https://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard"
    }
    
    for sport, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('events'):
                    # Grab the highest priority active game
                    game = data['events'][0]
                    status = game['status']['type']['detail']
                    home_team = game['competitions'][0]['competitors'][0]
                    away_team = game['competitions'][0]['competitors'][1]
                    
                    payload = {
                        "status": status,
                        "homeTeam": home_team['team']['abbreviation'],
                        "homeScore": home_team['score'],
                        "awayTeam": away_team['team']['abbreviation'],
                        "awayScore": away_team['score'],
                        "lastUpdated": datetime.now().isoformat()
                    }
                    
                    # Push directly to the D1 segment of the Firebase tree
                    ref = db.reference(f'live_games/d1/{sport}_global')
                    ref.set(payload)
                    print(f"   ☁️ Synced {sport.upper()}: {payload['awayTeam']} {payload['awayScore']} @ {payload['homeTeam']} {payload['homeScore']}")
                    
        except Exception as e:
            print(f"   ❌ API Error for {sport.upper()}: {e}")

# ==========================================
# 3. SCHEDULER
# ==========================================
# Run the sync every 30 seconds to avoid API rate limits
schedule.every(30).seconds.do(fetch_and_sync_espn)

print("🚀 Omni-Sport Python Pipeline Online...")
fetch_and_sync_espn() # Execute first run immediately

while True:
    schedule.run_pending()
    time.sleep(1)
