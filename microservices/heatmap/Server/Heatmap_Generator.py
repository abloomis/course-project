import matplotlib.pyplot as plt
from  matplotlib.colors import ListedColormap
import csv

# personal addition for formatting issue
import re

def makePlot(labels, winPct, scores, outputFilename, goodColor="#00FF00", midColor="#FFFF00", badColor="#FF0000"):
    plotSize = len(labels)

    cmap=ListedColormap([badColor, midColor, goodColor])
    cmap.set_under('gray')
    cmap.set_over('black')
    fig, ax = plt.subplots()

    plotFontSize = 15 if plotSize < 15 else 250//len(labels)
    plt.rcParams.update({'font.size': plotFontSize})

    ax.pcolor(winPct, edgecolors='k', cmap=cmap, linewidths=1, vmin=0, vmax=1)

    # UNCOMMENT FOR TEXT IN BOX
    if plotSize <= 10:
        for j, row in enumerate(scores):
            for i, txt in enumerate(row):
                x_offset = 0.5 - 0.05*(len(txt))*(plotSize/5)
                ax.annotate(txt, xy=(i+x_offset, j+0.575), fontsize=plotFontSize-3)

    ax.invert_yaxis()
    xticks = []
    yticks = []
    count = 0
    for _ in labels:
        xticks.append(count+0.5)
        yticks.append(count+0.5)
        count += 1
    plt.xticks(fontsize = plotFontSize)
    ax.set(xticks=xticks, xticklabels=labels)
    ax.set(yticks=yticks, yticklabels=labels)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.tick_params(axis=u'both', which=u'both',length=0, labelsize=plotFontSize)
    ax.tick_params(axis='x', labelrotation=90)

    # ax.set_title('Win percentage', pad=40)
    # ax.set_xlabel('Player')
    # ax.set_ylabel('Opponent')
    # ax.xaxis.set_label_position('top')

    plt.savefig(outputFilename, bbox_inches = 'tight')
    # plt.show()

def verifyCSV(filename):
    with open (filename, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        size = len(header)-1
        if size > 200:
            return False
        row_count = 0
        for row in csvreader:
            row_count += 1
            if (len(row)-1 != size):
                return False
        if (row_count != size):
            return False
    return True

def readCSV(filename):
    with open (filename, 'r') as file:
        csvreader = csv.reader(file)
        players = next(csvreader)[1:]
        size = len(players)
        scores = [[] for _ in range(size)]
        row_count = 0
        for row in csvreader:
            scores[row_count] = row[1:]
            row_count += 1
    return (players, scores)

# added by myself, helper function to parse scoring for multiple formats
# i.e. (3 -- 2) vs (3-2)
def parse_score(score):
    match = re.match(r'^\s*(\d+)\s*[-–]{1,2}\s*(\d+)\s*$', score)
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))

# modified to deal with formatting issue
def analyzeScores(scores):
    size = len(scores)
    winPct = [[None for _ in range(size)] for _ in range(size)]
    gamesPlayed = [[None for _ in range(size)] for _ in range(size)]
    for j, row in enumerate(scores):
        for i, score in enumerate(row):
            wins, losses = parse_score(score)
            thisGamesPlayed = wins + losses
            thisWinPct = wins / thisGamesPlayed if thisGamesPlayed > 0 else -1
            winPct[j][i] = thisWinPct
            gamesPlayed[j][i] = thisGamesPlayed
            if i == j:
                winPct[j][i] = 2
                gamesPlayed[j][i] = 0
    return (winPct, gamesPlayed)

def handle_request(inFilename, outFilename, colorString=''):
    if not verifyCSV(inFilename):
        return(False, "Error with input file.")
    else:
        (players, scores) = readCSV(inFilename)
        (winPct, gamesPlayed) = analyzeScores(scores)
        if colorString == '':
            makePlot(players, winPct, scores, outFilename)
        else:
            goodColor = colorString[:7]
            midColor = colorString[8:15]
            badColor = colorString[16:23]
            makePlot(players, winPct, scores, outFilename, goodColor, midColor, badColor)
        return(True, "See OutputChart.png for plotted data.")