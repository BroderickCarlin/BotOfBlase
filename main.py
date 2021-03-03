import requests
import os
import json

# Set this envvar to your Blaseball cookie
token_key = "BLASEBALL_TOKEN"

def get_user(cookie):
    r = requests.get('https://www.blaseball.com/api/getUser', cookies={"connect.sid": cookie})
    return r.json()

def get_active_bets(cookie):
    r = requests.get('https://www.blaseball.com/api/getActiveBets', cookies={"connect.sid": cookie})
    return r.json()

def get_games_to_bet_on(cookie):
    r = requests.get('https://www.blaseball.com/events/streamData', cookies={"connect.sid": cookie}, stream=True)
    if r.encoding is None:
        r.encoding = 'utf-8'

    for line in r.iter_lines(decode_unicode=True):
        if line:
            games = json.loads(line[6:])['value']['games']['tomorrowSchedule']
            return games
            
def bet_on_game(cookie, user_id, team_id, game_id, amount):
    body = json.dumps({u"amount": amount, u"userId": user_id, u"targets": [team_id, game_id], u"type": 0})
    headers = {"Host": "www.blaseball.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/json", "Origin": "https://www.blaseball.com", "Content-Length": "162", "Connection": "keep-alive", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Sec-GPC": "1"}
    r = requests.post('https://www.blaseball.com/api/bet', cookies={"connect.sid": cookie}, data=body, headers=headers)
    return r.status_code == 200


if __name__ == "__main__":
    cookie = os.getenv(token_key)
    user = get_user(cookie)
    bets = get_active_bets(cookie)
    games = get_games_to_bet_on(cookie)

    max_bet = 1000

    print("Have {} coins to bet".format(user["coins"]))

    for game in games:
        print("{} -- ({}){} vs ({}){}".format(game['id'],  game['homeTeam'], game['homeTeamName'],  game['awayTeam'], game['awayTeamName']))
        print("{}: {:.2f}% vs {}: {:.2f}%".format(game['homeTeamName'], game['homeOdds'] * 100, game['awayTeamName'], game['awayOdds'] * 100))
        user = get_user(cookie)
        bet = user["coins"] if user["coins"] < max_bet else max_bet

        if bet == 0:
            continue
        
        if game['homeOdds'] > game['awayOdds']:
            print("Betting on: {}".format(game['homeTeamName']))
            bet_on_game(cookie, user["id"], game['homeTeam'], game['id'], bet)
        else:
            print("Betting on: {}".format(game['awayTeamName']))
            bet_on_game(cookie, user["id"], game['awayTeam'], game['id'], bet)
        print("\n")
