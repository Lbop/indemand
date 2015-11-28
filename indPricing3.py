# The goal of this program is to iterate through a list of hd and sd
# assets and match them with pricing from a second csv file (EST Master List)
# Programmed by Derrick Olson 6/17/2015

# https://github.com/hzheng/pybox
# import pybox

# csv for working with input files

import csv

# time for dating when master list was last updated

import os.path, time

# Load fuzzywuzzy, documentation https://github.com/seatgeek/fuzzywuzzy

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Function to see if input is an HD title or not by looking to see if there is 
# an 'HD' string at the end of the title. breaks if last character is a space in input

def isHD(title):

# # strip out one blank spaces at highest index - breaks if there are two words and no extra space
# strippedTitle = title.rsplit(' ',1)[0]

# find length of title 
    titleLength = len(title)

    # find instance of HD at the highest index
    HDloc = title.lower().rfind('hd')

    # test to see if we found 'HD' string at end of title
    if HDloc > int(titleLength - 3):
        return 1
    else:
        return 0

# blank dictionary of full titles and pricing

sourcetitleList = []

SDtitleList = []
SDpricingList = {}

HDtitleList = []
HDpricingList = {}

sourcePricingListDict = {}

# Load CSV file and date it // create prompt for filename?

pricingFile = 'masterTest.csv'
sourceFile = 'masterTestSource.csv'
fileTime = time.ctime(os.path.getmtime(pricingFile))
 
# Open CSV file and create dictionary of pricing and list of titles for fuzzy match

with open(pricingFile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        fullTitle = row['Full Title']
        pricing = row['Retail']
        if isHD(fullTitle) == 1:
            HDtitleList.append(fullTitle.lower())
            HDpricingList.update({fullTitle.lower():pricing})
        else:
            SDtitleList.append(fullTitle.lower())
            SDpricingList.update({fullTitle.lower():pricing})

# open and load source list of titles

with open(sourceFile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader: 
        fullTitle = row['REVISED Full Title']
        pricing = row['MSO SRP (Scheme M) Comcast']
        sourcetitleList.append(fullTitle.lower())
        #added 7/1/15 to print indab pricing in output
        sourcePricingListDict.update({fullTitle.lower():pricing})
        
# use fuzzy logic to match title to pricing

for titles in sourcetitleList:
    searchTitle = titles
    if isHD(searchTitle) == 1:
        bestChoice = str(process.extract(searchTitle, HDtitleList, limit=1))
    else:
        bestChoice = str(process.extract(searchTitle, SDtitleList, limit=1))

# need to edit this to support apostrophes in titles            
    bestChoiceTitle = bestChoice.split("'")[1].split("'")[0]
    
# checks result to see if greater than 50% using token sort
    tokenSort = fuzz.token_sort_ratio(searchTitle, bestChoiceTitle)
    
    if tokenSort < 50:
    
        with open('PricingTEST.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([searchTitle, 'Suitable match not found.', 'No pricing as of %s.' % fileTime])
            
    else:
# Write list of matches to CSV file 
    
        with open('PricingTEST.csv', 'a') as f:
            writer = csv.writer(f)
            if isHD(searchTitle) == 1:
                writer.writerow([searchTitle, bestChoiceTitle, HDpricingList[bestChoiceTitle],tokenSort,sourcePricingListDict[searchTitle]])
            else:
                writer.writerow([searchTitle, bestChoiceTitle, SDpricingList[bestChoiceTitle],tokenSort,sourcePricingListDict[searchTitle]])
                
# Uses simple ratio fuzzy logic to compare complete strings
#fuzzRatio = fuzz.ratio(inputTitle, comparisonTitle)