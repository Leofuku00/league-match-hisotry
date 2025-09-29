import riot
from flask import Flask, redirect, render_template, request, url_for
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
api_key = "RGAPI-feaaebb2-273e-4b45-b6b4-9476519b1c97" 

riot.load_rune_data()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
@app.route("/", methods=["GET", "POST"])
def index():
    """Handles the user input form."""
    if request.method == "POST":
        username = request.form.get("username")
        tag = request.form.get("tag")
        if not username or not tag:
            return redirect("/")
        return redirect(url_for('summoner', username=username, tag=tag))
    return render_template("index.html")

@app.route("/summoner", methods=["GET"])
def summoner():
    """Fetches data and displays the match results."""
    username = request.args.get("username")
    tag = request.args.get("tag")
    if not username or not tag:
        return redirect("/")
    matchids,tierurl,tier,division,lp = riot.get_player_matchhistory(username, tag, api_key)
    all_data=[]
    for match in matchids:
        matchdata = riot.get_matchdata(match, api_key)
        playernames = riot.get_playernames(matchdata)
        summoner_match_info = riot.get_summoner_match_info(matchdata, username)
        match_info = riot.get_match_info(matchdata)
        player_dict = {name: url for name, url in zip(playernames, match_info["all_champs"])}
        match_data={"playernames":playernames,"player_dict":player_dict,"summoner_match_info":summoner_match_info,"match_info":match_info}
        all_data.append(match_data)
    return render_template("summoner.html", all_data=all_data,username=username,tag=tag,icon_url=all_data[0]["summoner_match_info"]["icon_url"],tierurl=tierurl,tier=tier,division=division,lp=lp)