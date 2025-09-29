import os
import requests
import time
import pandas as pd
import json

def get_player_matchhistory(username,tag,apikey):
    api_url="https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+username+"/"+tag+"?api_key="+apikey
    while True:
        results=requests.get(api_url)
        if results.status_code==429:
            time.sleep(10)
            continue
        break
    results=results.json()
    puid=results['puuid']
    api_url="https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puid+"/ids?start=0&count=10&api_key="+apikey
    while True:
        matchids=requests.get(api_url)
        if matchids.status_code==429:
            time.sleep(10)
            continue
        break
    matchids=matchids.json()
    print(matchids)
    api_url="https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/"+puid+"?api_key="+apikey
    while True:
        sumdata=requests.get(api_url)
        if sumdata.status_code==429:
            time.sleep(10)
            continue
        break
    sumdata=sumdata.json()
    for data in sumdata:
        if data["queueType"]=="RANKED_SOLO_5x5":
            tier=data["tier"]
            division=data["rank"]
            lp=data["leaguePoints"]
            tierurl="https://opgg-static.akamaized.net/images/medals_new/"+tier.lower()+".png"
        else:
            tierurl="https://static.wikia.nocookie.net/leagueoflegends/images/1/13/Season_2023_-_Unranked.png"
    print(tierurl)
    return matchids,tierurl,tier,division,lp

def get_matchdata(matchid,apikey):
    api_url="https://americas.api.riotgames.com/lol/match/v5/matches/"+matchid+"?api_key="+apikey
    while True:
        matchdata=requests.get(api_url)
        if matchdata.status_code==429:
            time.sleep(10)
            continue
        break
    matchdata=matchdata.json()
    return matchdata

def get_playernames(matchdata):
    0,5,1,6,2,7,3,8,4,9
    playernames=[]
    for x in range(0,10):
        playernames.append(matchdata["info"]["participants"][x]["riotIdGameName"]+"#"+matchdata["info"]["participants"][x]["riotIdTagline"])
    sorted_names=[]
    t1=playernames[:5]
    t2=playernames[5:]
    for x in range(0,10):
        if x%2==0:
            sorted_names.append(t1[int(x/2)])
        else:
            sorted_names.append(t2[int(x/2)])
    return sorted_names



KEYSTONES_BY_ID = {}
TREES_BY_ID = {}
BASE_IMG_URL = "https://ddragon.leagueoflegends.com/cdn/img"

def load_rune_data():
    """
    Reads the local JSON file and populates the global lookup tables.
    Run this function ONCE when your application starts.
    """
    global KEYSTONES_BY_ID, TREES_BY_ID
    
    try:
        with open("runesReforged.json", "r", encoding="utf-8") as f:
            all_runes_data = json.load(f)
    except FileNotFoundError:
        return

    KEYSTONES_BY_ID = {
        rune['id']: rune 
        for tree in all_runes_data 
        for rune in tree['slots'][0]['runes']
    }
    TREES_BY_ID = {
        tree['id']: tree 
        for tree in all_runes_data
    }


def getrune_url(primary_keystone_id, secondary_tree_id):
    primary_rune_data = KEYSTONES_BY_ID.get(primary_keystone_id)
    secondary_tree_data = TREES_BY_ID.get(secondary_tree_id)
    primary_url = None
    secondary_url = None
    if primary_rune_data:
        primary_icon = primary_rune_data['icon']
        primary_url = f"{BASE_IMG_URL}/{primary_icon}"
    
    if secondary_tree_data:
        secondary_icon = secondary_tree_data['icon']
        secondary_url = f"{BASE_IMG_URL}/{secondary_icon}"

    return primary_url, secondary_url

def get_champion_image_url(champion_name):
    DATA_DRAGON_URL = "https://ddragon.leagueoflegends.com/cdn/15.19.1/img/champion/"
    champion_name = champion_name.replace("'", "").replace(".", "").replace(" ", "")
    if champion_name=="FiddleSticks":
        champion_name="Fiddlesticks"
    return f"{DATA_DRAGON_URL}{champion_name}.png"

def get_profile_url(profile):
    DATA_DRAGON_URL = "https://ddragon.leagueoflegends.com/cdn/15.19.1/img/profileicon/"
    champion_name = champion_name.replace("'", "").replace(".", "").replace(" ", "")
    if champion_name=="FiddleSticks":
        champion_name="Fiddlesticks"
    return f"{DATA_DRAGON_URL}{champion_name}.png"

def get_item_image_url(items):
    itemurls = []
    for item_id in items:
        if item_id == 0:
            itemurls.append(None)
        else:
            DATA_DRAGON_URL = "https://ddragon.leagueoflegends.com/cdn/15.19.1/img/item/"
            item_url = DATA_DRAGON_URL + str(item_id) + ".png"
            itemurls.append(item_url)
    return itemurls

QUEUE_ID_MAP = {
    400: "Normal Draft",
    420: "Ranked Solo/Duo",
    430: "Normal Blind",
    440: "Ranked Flex",
    450: "ARAM",
    490: "Quick Play",
    1700: "Arena"
}

def get_match_info(matchdata):
    queueid=matchdata["info"]["queueId"]
    mode = QUEUE_ID_MAP.get(queueid).upper()
    print(mode)
    gameduration=matchdata["info"]["gameDuration"]
    minute,second=divmod(gameduration,60)
    duration=str(minute)+"m "+str(second)+"s"
    all_champs=[]
    for x in range(0,10):
        champname=matchdata["info"]["participants"][x]["championName"]
        all_champs.append(champname)
    sorted_champs=[]
    t1=all_champs[:5]
    t2=all_champs[5:]
    for x in range(0,10):
        if x%2==0:
            sorted_champs.append(t1[int(x/2)])
        else:
            sorted_champs.append(t2[int(x/2)])
    all_champs_urls = [get_champion_image_url(champ) for champ in sorted_champs]
    match_info={"mode":mode,"duration":duration,"all_champs":all_champs_urls}
    return match_info

def get_summoner_match_info(matchdata,username):
    wl="Defeat"
    for x in range(0,10):
        if matchdata["info"]["participants"][x]["riotIdGameName"]==username:
            if matchdata["info"]["participants"][x]["win"]==True:
                wl="Victory"
            if matchdata["info"]["gameDuration"]<180:
                wl="Remake"
                print('error here')
            items=[]
            champ=matchdata["info"]["participants"][x]["championName"]
            items.append(matchdata["info"]["participants"][x]["item0"])
            items.append(matchdata["info"]["participants"][x]["item1"])
            items.append(matchdata["info"]["participants"][x]["item2"])
            items.append(matchdata["info"]["participants"][x]["item3"])
            items.append(matchdata["info"]["participants"][x]["item4"])
            items.append(matchdata["info"]["participants"][x]["item5"])
            items.append(matchdata["info"]["participants"][x]["item6"])
            kills=matchdata["info"]["participants"][x]["kills"]
            deaths=matchdata["info"]["participants"][x]["deaths"]
            assists=matchdata["info"]["participants"][x]["assists"]
            icon=matchdata["info"]["participants"][x]["profileIcon"]
            summoner_level=matchdata["info"]["participants"][x]["summonerLevel"]
            icon_url="https://ddragon.leagueoflegends.com/cdn/15.19.1/img/profileicon/"+str(icon)+".png"
            kda=str(kills)+"/"+str(deaths)+"/"+str(assists)
            try:
                kdadec= (kills+assists)/deaths
                kdadec=f"{kdadec:.2f}"
            except ZeroDivisionError:
                kdadec="Perfect"
            ss={
                1:"Boost",
                3:"Exhaust",
                4:"Flash",
                6:"Haste",
                7:"Heal",
                11:"Smite",
                12:"Teleport",
                13:"Mana",
                14:"Dot",
                21:"Barrier",
                30:"PoroRecall",
                31:"PoroThrow",
                32:"Snowball",
                54:"_UltBookPlaceholder",
                55:"_UltBookSmitePlaceholder",
                2201:"CherryHold",
                2202:"CherryFlash"
            }
            ss1=matchdata["info"]["participants"][x]["summoner1Id"]
            ss2=matchdata["info"]["participants"][x]["summoner2Id"]
            ss1url="https://ddragon.leagueoflegends.com/cdn/15.19.1/img/spell/Summoner"+ss[ss1]+".png"
            ss2url="https://ddragon.leagueoflegends.com/cdn/15.19.1/img/spell/Summoner"+ss[ss2]+".png"
            level=matchdata["info"]["participants"][x]["champLevel"]
            keystone = matchdata["info"]["participants"][x]["perks"]['styles'][0]['selections'][0]['perk']
            secondary_keystone=matchdata["info"]["participants"][x]["perks"]['styles'][1]['style']
            keystone_url,secondary_keystone_url=getrune_url(keystone,secondary_keystone)
            

    item_urls = get_item_image_url(items)
    playerchamp_url = get_champion_image_url(champ)
    summoner_match_info={"result":wl,"playerchamp_url":playerchamp_url,"item_urls":item_urls,"kda":kda,"kdadec":kdadec,"ss1url":ss1url,"ss2url":ss2url,"keystone_url":keystone_url,"secondary_keystone_url":secondary_keystone_url,"level":level,"icon_url":icon_url,"summoner_level":summoner_level}
    return summoner_match_info


