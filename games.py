#!/usr/bin/env python3
import csv
import re

# make dictionary linking team IDs to actual names 

teams = {}

with open('teams.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader:
        if (rowCount > 0):
            teams[row[1]] = row[5]
        else:
            rowCount += 1

# see correlation between higher field goal percentage and win rate 

highFGwin = 0 # number of games where team with higher fg% wins
high3win = 0 # number of games where team with higher 3p% wins
highFTwin = 0

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader:
        if(rowCount == 0):
            rowCount += 1
        elif(rowCount < 1291):  
            diffFG = float(row[8]) - float(row[15])
            diff3 = float(row[10]) - float(row[17])
            diffFT = float(row[9]) - float(row[16])

            if('1' in row[20] and diffFG > 0.0):
                highFGwin += 1
            if('0' in row[20] and diffFG < 0.0):
                highFGwin += 1

            if('1' in row[20] and diff3 > 0.0):
                high3win += 1
            if('0' in row[20] and diff3 < 0.0):
                high3win += 1

            if('1' in row[20] and diffFT > 0.0):
                highFTwin += 1
            if('0' in row[20] and diffFT < 0.0):
                highFTwin += 1
            
            rowCount += 1

correlationFG = float(highFGwin) / 1290
correlation3 = float(high3win) / 1290
correlationFT = float(highFTwin) / 1290
"""print(correlationFG)
print(correlation3)
print(correlationFT)"""

# ********
# MASTER PLAN V1 - Strength of schedule adjustment 
    # For every opponent a team has played 
        # Defense 
            # Calculate the oppoenent's average score against other teams, find difference between that avg and how much the team gave up
            # Average all these differences to get a feel for defensive effectiveness 
        # Offense (reverse of defense)
            # Calculate the opponent's average scored allowed against other teams, find difference between that avg and how much the team gave up 
            # Average all these differences to get a feel for offensive effectiveness 

    # Do this for both teams, then add these differences to get an expected score 
    # Use standard deviations to figure out volatility and find confidence intervals for expected scores
    # Figure out fouls called per ref and adjust to give favor to teams that get fouled a lot/shoot FTs well (find correlations for that adjustment)
# ********


# find AWAY points and points allowed for each team for each game 

teamA_pts = {} #keys = team names, values = array of points in each game 
teamA_allowed = {}
teamA_IDs = [] #list of IDs to track whether used or not

teamAvgs = {}
teamAvgsAllowed = {}

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount < 502): #skip 20/21 and bubble games, only grab 19/20 games thru January (to test predictions for feb/march)
            rowCount += 1
        elif(rowCount < 1226):
            teamID = row[4]
            team = teams[teamID]
            if teamID not in teamA_IDs:
                teamA_IDs.append(teamID)
                teamA_pts[team] = []
                teamA_allowed[team] = []
            
            teamA_pts[team].append(row[14])
            teamA_allowed[team].append(row[7])
            rowCount += 1

    # make dict of averages 
    for key in teamA_pts.keys():
        teamTotal = 0.0
        for pts in teamA_pts[key]:
            pts = float(pts)
            teamTotal += pts
            teamAvg = round((teamTotal / len(teamA_pts[key])),4)
            teamAvgs[key] = teamAvg
    
    for key in teamA_allowed.keys():
        teamTotalAllowed = 0.0
        for allowed in teamA_allowed[key]:
            allowed = float(allowed)
            teamTotalAllowed += allowed
            teamAvgAllowed = round((teamTotalAllowed / len(teamA_allowed[key])),4)
            teamAvgsAllowed[key] = teamAvgAllowed

    
    #print(teamAvgsAllowed)

# find HOME points and points allowed for each team for each game 

teamH_pts = {}
teamH_allowed = {}
teamH_IDs = []

teamHavgs = {}
teamHavgs_allowed = {}

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount < 502): 
            rowCount += 1
        elif(rowCount < 1226):
            teamID = row[3]
            team = teams[teamID]
            if teamID not in teamH_IDs:
                teamH_IDs.append(teamID)
                teamH_pts[team] = []
                teamH_allowed[team] = []
            
            teamH_pts[team].append(row[7])
            teamH_allowed[team].append(row[14])
            rowCount += 1

    # make dict of averages 
    for key in teamH_pts.keys():
        teamTotal = 0.0
        for pts in teamH_pts[key]:
            pts = float(pts)
            teamTotal += pts
            teamAvg = round((teamTotal / len(teamH_pts[key])),4)
            teamHavgs[key] = teamAvg

    for key in teamH_allowed.keys():
        teamTotalAllowed = 0.0
        for pts in teamH_allowed[key]:
            pts = float(pts)
            teamTotalAllowed += pts
            teamAvg = round((teamTotalAllowed / len(teamH_allowed[key])),4)
            teamHavgs_allowed[key] = teamAvg

# find points - expected points (opponent's pts allowed) for AWAY 
# find points allowed - exp. points allowed for AWAY 

teamA_odiffs = {} #offensive diff
teamA_ddiffs = {} #defensive diff
teamA_ids = []

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount < 502): #skip 20/21 and bubble games, only want original 19/20 games 
            rowCount += 1
        elif(rowCount < 1226):
            teamID = row[4]
            team = teams[teamID]
            opponent = teams[row[3]]
            if teamID not in teamA_ids:
                teamA_ids.append(teamID)
                teamA_odiffs[team] = []
                teamA_ddiffs[team] = []

            rowCount += 1
            
            teamA_odiffs[team].append(float(row[14]) - teamHavgs_allowed[opponent]) #how much you score - how much opponent usually allows
            teamA_ddiffs[team].append(float(row[7]) - teamHavgs[opponent]) #how much opponent scored - how much they usually score


# find points - expected points (opponent's pts allowed) for HOME
#find points allowed - exp. points allowed for HOME

teamH_odiffs = {}
teamH_ddiffs = {}
teamH_ids = []

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount < 502): #skip 20/21 and bubble games, only want original 19/20 games 
            rowCount += 1
        elif(rowCount < 1226):
            teamID = row[3]
            team = teams[teamID]
            opponent = teams[row[4]]
            if teamID not in teamH_ids:
                teamH_ids.append(teamID)
                teamH_odiffs[team] = []
                teamH_ddiffs[team] = []

            rowCount += 1
            
            teamH_odiffs[team].append(float(row[7]) - teamAvgsAllowed[opponent]) #how much you score - how much opponent usually allows
            teamH_ddiffs[team].append(float(row[14]) - teamAvgs[opponent]) #how much opp scored - how much they usually score
        

# find average off and def differential for each team 

homeOffAvgs = {}
homeDefAvgs = {}
awayOffAvgs = {}
awayDefAvgs = {}

for team in teamH_odiffs:
    homeOffAvgs[team] = round(sum(teamH_odiffs[team])/len(teamH_odiffs[team]),3)

for team in teamH_ddiffs:
    homeDefAvgs[team] = round(sum(teamH_ddiffs[team])/len(teamH_ddiffs[team]),3)

for team in teamA_odiffs:
    awayOffAvgs[team] = round(sum(teamA_odiffs[team])/len(teamA_odiffs[team]),3)

for team in teamA_ddiffs:
    awayDefAvgs[team] = round(sum(teamA_ddiffs[team])/len(teamA_ddiffs[team]),3)

#predictions 

results = [] # date, away team, home team, pred. away score, pred. home score, actual away score, actual home score

with open('games.csv') as csv_file: 
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount < 255): #skip 20/21 and bubble games, only want original 19/20 games 
            rowCount += 1
        elif(rowCount < 1226):
            
            date = row[0]
            cut = re.split("/", date, 2)
            month = cut[0]
            day = cut[1]

            if float(day) < 10:
                day = "0" + day

            newDate = month + day

            homeID = row[3]
            awayID = row[4]
            home = teams[homeID]
            away = teams[awayID]
            
            predAway = round( ( ( (teamAvgs[away] + homeDefAvgs[home]) + (teamHavgs_allowed[home] + awayOffAvgs[away]) ) / 2 ), 2)
            predHome = round( ( ( (teamHavgs[home] + awayDefAvgs[away]) + (teamAvgsAllowed[away] + homeOffAvgs[home]) ) / 2), 2)

            actualAway = float(row[14])
            actualHome = float(row[7])

            results.append([newDate, away, home, predAway, predHome, actualAway, actualHome])

            rowCount += 1

results.reverse()

# get data from odds list: Date, spread odds, home team

oddsList = []
gameCount = 0
spread = False

with open('odds1920.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    rowCount = 0
    for row in csv_reader: 
        if(rowCount == 0):
            rowCount += 1
        elif(rowCount < 1943):
            if(rowCount %2 != 0):
                spread = False 

                numSpread = row[10]
                if(numSpread == 'pk'):
                    numSpread = float(0)
                else:
                    numSpread = float(numSpread)
                
                if(float(numSpread) < 100):
                    spread = True 
                    oddsList.append([ row[0], numSpread ])
            if(rowCount % 2 == 0): #even rows, shows visiting team 
                homeTeam = row[3]
                
                if not spread:
                    numSpread = row[10]
                    if(numSpread == 'pk'):
                        numSpread = float(0)
                    else:
                        numSpread = float(numSpread)

                    if(float(row[11]) < 0): 
                        numSpread = numSpread * -1
                        oddsList.append([ row[0], numSpread, homeTeam])
                else:
                    oddsList[gameCount].append(homeTeam)
                    
               
                gameCount += 1
                
            
            rowCount += 1

# dictionary to change oddsList team city names into team nicknames ( so we can match with team nicknames in results)
teamNames = {
    "Atlanta": "Hawks",
    "Chicago": "Bulls",
    "Milwaukee": "Bucks",
    "NewYork": "Knicks",
    "Cleveland": "Cavaliers",
    "Detroit": "Pistons",
    "Toronto": "Raptors",
    "Minnesota": "Timberwolves",
    "Phoenix": "Suns",
    "LALakers": "Lakers",
    "LAClippers": "Clippers",
    "Houston": "Rockets",
    "Dallas": "Mavericks",
    "Sacramento": "Kings",
    "Brooklyn": "Nets",
    "Orlando": "Magic",
    "Miami": "Heat",
    "Portland": "Trail Blazers",
    "Denver": "Nuggets",
    "Utah": "Jazz",
    "Charlotte": "Hornets",
    "NewOrleans": "Pelicans",
    "Boston": "Celtics",
    "Memphis": "Grizzlies",
    "OklahomaCity": "Thunder",
    "GoldenState": "Warriors",
    "SanAntonio": "Spurs",
    "Philadelphia": "76ers",
    "Indiana": "Pacers",
    "Washington": "Wizards"
    }

for ogm in oddsList: 
    for city in teamNames.keys():
        if ogm[2] == city:
            ogm[2] = teamNames[city]
    
# compare oddsList with predictions and actual game results to see how often prediction was correct 
homeCoverPredict = False
homeCoverResult = False

#testing
numHomeCoverPredict = 0
numAwayCoverPredict = 0

numHomeCovers = 0
numAwayCovers = 0

correct = 0

for ogm in oddsList:
    for rgm in results:
        if(ogm[0] == rgm[0] and ogm[2] == rgm[2]): # if dates and teams are equal (i.e. for each game)
            spread = float(ogm[1])
            predMargin = rgm[4] - rgm[3]
           
            if(spread <= 0 and predMargin < 0): #if home team is favored and prediction is away team favored 
                homeCoverPredict = False
            elif(spread <= 0 and predMargin > 0): #if home team is favored and prediction is home team favored
                if(predMargin > abs(spread)):
                    homeCoverPredict = True 
                    numHomeCoverPredict += 1
                else:
                    homeCoverPredict = False 
            elif(spread >= 0 and predMargin > 0): #if home team is underdogs and prediction is home team favored 
                homeCoverPredict = True
                numHomeCoverPredict += 1
            elif(spread >= 0 and predMargin < 0): #if home team is underdogs and prediction is away team favored
                if(abs(predMargin) < spread):
                    homeCoverPredict = True
                    numHomeCoverPredict += 1
                else:
                    homeCoverPredict = False


            actualMargin = rgm[6] - rgm[5]
            
            if(spread <= 0 and actualMargin < 0): #if home team is favored and prediction is away team favored 
                homeCoverResult = False
            elif(spread <= 0 and actualMargin > 0): #if home team is favored and prediction is home team favored
                if(actualMargin > abs(spread)):
                    homeCoverResult = True 
                    numHomeCovers += 1
                else:
                    homeCoverResult = False 
            elif(spread >= 0 and actualMargin > 0): #if home team is underdogs and prediction is home team favored 
                homeCoverResult = True
                numHomeCovers += 1
            elif(spread >= 0 and actualMargin < 0): #if home team is underdogs and prediction is away team favored
                if(abs(actualMargin) < spread):
                    homeCoverResult = True
                    numHomeCovers += 1
                else:
                    homeCoverResult = False

            
            if(homeCoverPredict and homeCoverResult):
                correct += 1
            elif(not homeCoverPredict and not homeCoverResult):
                correct += 1
            
print(numHomeCovers)
print(numHomeCoverPredict)


pctCorrect = correct / 971.0
print(pctCorrect)





    







    

