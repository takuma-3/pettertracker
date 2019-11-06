import requests, threading, json, os, time

#Api specs (id 23 = canucks)
rootUrl = 'https://statsapi.web.nhl.com'
nextGameApi = '/api/v1/teams/23?expand=team.schedule.next'
PATTERSON_ID = '8480012'

#Definitions
DEF_ON_ALERT = " - OH MY GOD ITS HAPPENNING, PATTERSON IS ON THE ICE!!"
DEF_OFF_ALERT = " - PATTERSON IS OFF THE ICE?! WHAT THE HECK"
DEF_NOT_LIVE = " - Game is not live"
DEF_INIT = " - Initializing..."

ERR_NO_INTERNET = "Failed to connect, check your internet connection"

#StatusCodes for PlayerState management
statusCode_NOT_LIVE = "NL"
statusCode_ON_ICE = "OI"
statusCode_OFF_ICE = "OF"
statusCode_INIT = "INIT"
statusCode_ERR = "ERR"

#Class to track states between different times
class PlayerState:
    def __init__(self, statusCode, message, errFlag):
        self.statusCode = statusCode
        self.message = message
        self.errFlag = errFlag

#Function 
def isPattersonOn(playerState):
    response = requests.get(rootUrl + nextGameApi,params='')
    if(response.ok):
        #Successful to connect
        rJsonObj = toJson(response)
        nextGameDate = rJsonObj['teams'][0]['nextGameSchedule']['dates'][0]['date']
        nextGamePk = rJsonObj['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['gamePk']
        gameFeedLink = rJsonObj['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['link']
        gameStatus = rJsonObj['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['status']['abstractGameState']
        if(gameStatus != 'Live'):
            print(DEF_NOT_LIVE)
            return createPlayerState(statusCode_NOT_LIVE,DEF_NOT_LIVE,False)
        else:
            print(" Next game airdate is on: " + nextGameDate + "\n Game key is: " + str(nextGamePk) + "\n GameFeed: " + gameFeedLink)
            if(detectPatterson(gameFeedLink)):
                print("HES ON!")
                return createPlayerState(statusCode_ON_ICE,DEF_ON_ALERT,False)
            else:
                print("HES NOT ON!")
                return createPlayerState(statusCode_OFF_ICE,DEF_OFF_ALERT,False)
    else:
        #Failed to connect
        #print("Failed to connect, check your internet connection")
        return createPlayerState(statusCode_ERR,ERR_NO_INTERNET,True)

def createPlayerState(statusCode, message, errFlag):
    playerState = PlayerState(statusCode,message,errFlag)
    return playerState

#Pettersson id = 8480012
#Compare onIce list with playerid
def detectPatterson(liveLink):
    response = requests.get(rootUrl + liveLink,params='')
    rJsonObj = toJson(response)
    awayTeam = rJsonObj['liveData']['boxscore']['teams']['away']
    homeTeam = rJsonObj['liveData']['boxscore']['teams']['home']
    awayOnIce = awayTeam['onIce']
    homeOnIce = homeTeam['onIce']
    awayAndHomeOnIce = awayOnIce + homeOnIce
    if(parseList(PATTERSON_ID, awayAndHomeOnIce)):
        return True
    else:
        return False

#Is playerId in the list of "onIce" players
def parseList(playerId, playerList):
    print('PlayerID: ' + playerId)
    print('OnIce PlayerList: ')
    print(playerList)
    if int(playerId) in playerList :
        return True
    else:
        return False

#requires sudo apt install speech-dispatcher
def playAlert(words):
    os.system('say "' + words + '"')


#Return json obj from reponse
def toJson(response):
    rJsonObj = json.loads(response.content)
    return rJsonObj

#Play notification alery if and only if the statusCodes vary
def notificationManager(currentState, previousState):
    if(currentState.statusCode != previousState.statusCode):
        playAlert(currentState.message)


#Program entry point
def main():
    print("Starting Patterson Tracking.......")
    previousState = createPlayerState(statusCode_INIT,DEF_INIT,False)
    try:
        while True:
            currentState = isPattersonOn(previousState)
            notificationManager(currentState,previousState)
            previousState = currentState
            if(currentState.errFlag):
                Exitting
            time.sleep(5)
    except KeyboardInterrupt:
        print('Manual break by user')

main()




    

