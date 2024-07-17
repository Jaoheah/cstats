#!/usr/bin/python3

import json
import requests
import platform
import sys
from datetime import datetime

version = "0.1.0pre"

if platform.system() == 'Windows':
    # make color codes show up on windows properly, this library is not required on linux/mac
    from colorama import just_fix_windows_console
    just_fix_windows_console()

def ccparser(s):
    # this is very jank feeling but it works i guess
    s = s.replace("&", "§")
    
    s = s.replace("§0", "\033[30m")
    s = s.replace("§1", "\033[34m")
    s = s.replace("§2", "\033[32m")
    s = s.replace("§3", "\033[36m")
    s = s.replace("§4", "\033[31m")
    s = s.replace("§5", "\033[35m")
    s = s.replace("§6", "\033[33m")
    s = s.replace("§7", "\033[37m")
    s = s.replace("§8", "\033[90m")
    s = s.replace("§9", "\033[94m")
    s = s.replace("§a", "\033[92m")
    s = s.replace("§b", "\033[96m")
    s = s.replace("§c", "\033[91m")
    s = s.replace("§d", "\033[95m")
    s = s.replace("§e", "\033[93m")
    s = s.replace("§f", "\033[97m")

    s = s + "\033[0m"    
    return s

def uuidtousername(uuid):
    mojangapiurl = "https://sessionserver.mojang.com/session/minecraft/profile/" + uuid

    try:
        request = json.loads(json.dumps(requests.get(mojangapiurl).json()))
        username = request["name"]
    except:
        username = uuid

    return username

def usernametouuid(username):
    mojangapiurl = "https://api.mojang.com/users/profiles/minecraft/" + username

    request = json.loads(json.dumps(requests.get(mojangapiurl).json()))
    
    uuid = request["id"]
    uuidwithdashes = uuid[:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20] + "-" + uuid[20:]

    return uuidwithdashes

def fixusernamecase(username):
    mojangapiurl = "https://api.mojang.com/users/profiles/minecraft/" + username
    request = json.loads(json.dumps(requests.get(mojangapiurl).json()))

    usernamefixed = request["name"]
    return usernamefixed

def playerlist():
    listfmt = "{display} | {user} | {uuid} | X:{xcoord}, Y:{ycoord}, Z:{zcoord}"
    request = json.loads(json.dumps(requests.get('http://api.retromc.org/api/v1/server/players').json()))

    print("\033[94mThere are \033[91m" + str(request["player_count"]) + "\033[94m out of a maximum \033[91m100\033[94m players online.\033[0m\n\nOutput format:")
    print("Rank and display name | Username | Player UUID | X coord | Y coord | Z coord\n")

    for i in range(0, request["player_count"]):
        print(listfmt.format(
            display = ccparser(request['players'][i]['display_name']),
            user = request['players'][i]['name'], 
            uuid = request['players'][i]['uuid'], 
            xcoord = str(round(request['players'][i]['x'], 1)),
            ycoord = str(round(request['players'][i]['y'], 1)),
            zcoord = str(round(request['players'][i]['z'], 1))
        ))

def chat():
    listfmt = "{display}: {message}"
    request = json.loads(json.dumps(requests.get('http://api.retromc.org/api/v1/server/chat').json()))

    print("\033[94mDisplaying recently sent messages. (does \033[91mNOT\033[94m display Discord messages)\033[0m")

    for i in range(0, len(request['messages'])): 
        print(listfmt.format(
            display = ccparser(request['messages'][i]['display_name']), 
            message = ccparser(request['messages'][i]['message'])
        ))

def villagelist():
    listfmt = "{name} | {owner} | {villageuuid}"
    request = json.loads(json.dumps(requests.get('http://api.retromc.org/api/v1/village/getVillageList').json()))

    print("Displaying list of all RetroMC villages.\n\nOutput format:")
    print("Village name | Village owner | Village UUID\n")

    for i in range(0, len(request['villages'])): 
        print(listfmt.format(
            name = request['villages'][i]['name'], 
            owner = uuidtousername(request['villages'][i]['owner']),
            villageuuid = request['villages'][i]['uuid']
        ))

def villagedetails():
    print("Enter the village name:")
    village = input("> ").lower()

    request = json.loads(json.dumps(requests.get('http://api.retromc.org/api/v1/village/getVillageList').json()))

    print("\033[94mDisplaying village info.\033[0m")

    for i in range(0, len(request['villages'])): 
        if request['villages'][i]['name'].lower() == village:
            villageuuid = request['villages'][i]['uuid']
            break
    else:
        print("Village not found")
        return

    request2 = json.loads(json.dumps(requests.get('http://api.retromc.org/api/v1/village/getVillage?uuid=' + villageuuid).json()))
    
    print("Name: " + str(request2["name"]))
    print("Village UUID: " + str(request2["uuid"]))
    print("Owner: " + uuidtousername(request2['owner']))
    print("Location: X:" + str(request2["spawn"]["x"]) + ", Y:" + str(request2["spawn"]["y"]) + ", Z:" + str(request2["spawn"]["z"]) + " in world " + request2["spawn"]["world"])

    if request2['creationTime'] != 1640995200:
        print("Creation time: " + datetime.fromtimestamp(request2['creationTime']).strftime('%Y-%m-%d %H:%M:%S'))
    else:
        print("Creation time: Unknown (likely lost in Towny > JVillage transfer)")
        
    print("Balance: " + str(round(request2["balance"], 2)))
    print("Claim count: " + str(request2["claims"]))
    print("Assistants: " + str(len(request2["assistants"])))
    print("Members: " + str(len(request2["members"])))

    print("\nVillage flags: ")
    print("Members can invite: " + str(request2["flags"]["MEMBERS_CAN_INVITE"]))
    print("Random can alter: " + str(request2["flags"]["RANDOM_CAN_ALTER"]))
    print("Mobs can spawn: " + str(request2["flags"]["MOBS_CAN_SPAWN"]))
    print("Assistant can withdraw: " + str(request2["flags"]["ASSISTANT_CAN_WITHDRAW"]))
    print("Mob spawner bypass: " + str(request2["flags"]["MOB_SPAWNER_BYPASS"]))

    print("\nAssistants:")
    if len(request2["assistants"]) != 0:    
        for i in range(0, len(request2["assistants"])):
            print(uuidtousername(request2["assistants"][i]), end="")
            if len(request2["assistants"]) - 1 != i:
                print(", ", end="")
    else:
        print("No assistants", end="")

    print("\n\nMembers:")
    if len(request2["members"]) != 0:
        for i in range(0, len(request2["members"])):
            print(uuidtousername(request2["members"][i]), end="")
            if len(request2["members"]) - 1 != i:
                print(", ", end="")
    else:
        print("No members", end="")

    # Add newline to the end of the members output
    print("")

def playerstats():
    print("Enter the player name:")
    player = input("> ")
    playerusernamefixed = fixusernamecase(player)
    playeruuid = usernametouuid(playerusernamefixed)

    request = json.loads(json.dumps(requests.get('https://statistics.retromc.org/api/online?username=' + playerusernamefixed).json()))

    print("\033[94mDisplaying player info.\033[0m")

    print("Name: " + playerusernamefixed)
    print("Player UUID: " + playeruuid + "\n")
    
    print("Online: " + str(request["online"]))

    try:
        x = str(request["x"])
        y = str(request["x"])
        z = str(request["x"])
    except:
        x = "Player is offline"
        y = x
        z = x

    print("X: " + x)
    print("Y: " + y)
    print("Z: " + z)

    request2 = json.loads(json.dumps(requests.get('https://statistics.retromc.org/api/bans?uuid=' + str(playeruuid)).json()))

    print("\nBanned: " + str(request2["banned"]))

    print("Ban history: ")
    
    for i in range(len(request2["bans"])):
        print(request2["bans"][i]["admin"][0])

    request3 = json.loads(json.dumps(requests.get('https://statistics.retromc.org/api/user_villages?uuid=' + str(playeruuid)).json()))

    print("\nOwner of villages: ")
    if len(request3["data"]["owner"]) == 0:
        print("None :(")
    else:
        for i in range(len(request3["data"]["owner"])):
            print(request3["data"]["owner"][i]["village"] + " (" + request3["data"]["owner"][i]["village_uuid"] + ")")

    print("\nAssistant of villages: ")
    if len(request3["data"]["assistant"]) == 0:
        print("None :(")
    else:
        for i in range(len(request3["data"]["assistant"])):
            print(request3["data"]["assistant"][i]["village"] + " (" + request3["data"]["assistant"][i]["village_uuid"] + ")")

    print("\nMember of villages: ")
    if len(request3["data"]["member"]) == 0:
        print("None :(")
    else:
        for i in range(len(request3["data"]["member"])):
            print(request3["data"]["member"][i]["village"] + " (" + request3["data"]["member"][i]["village_uuid"] + ")")


def main():
    if len(sys.argv) > 1:
        choose = sys.argv[1]
    else:
        print("Welcome to cstats v" + version + "!")
        print("Type the name of a function or its numerical ID from the list below and press ENTER\n")
        
        print("1) playerlist")
        print("2) chat")
        print("3) villagelist")
        print("4) villagedetails")
        print("5) playerstats (WIP)")
        print("0) exit")

        print("\nThis program is still a work in progress, report issues to SvGaming")

        choose = input("> ")

    if choose == "1" or choose == "playerlist":
        playerlist()
    elif choose == "2" or choose == "chat":
        chat()
    elif choose == "3" or choose == "villagelist":
        villagelist()
    elif choose == "4" or choose == "villagedetails":
        villagedetails()
    elif choose == "5" or choose == "playerstats":
        playerstats()
    elif choose == "0" or choose == "exit":
        return
    else:
        print("Invalid option!")

if __name__ == '__main__':
    main()
