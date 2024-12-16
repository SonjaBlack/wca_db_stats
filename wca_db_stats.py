# wca_db_stats.py -- crappy tool for pulling various status out of a
# wca database export


import argparse
from collections import defaultdict
import csv
import re

# helper routine to format results as mm:ss.xx
def resultToTimeStr(result):
    seconds = int(result/100)
    centis = result % 100
    if seconds > 59:
        minutes = int(seconds/60)
        seconds = seconds%60
    else:
        minutes = 0
    if minutes == 0:
        return f"{seconds}.{centis:02d}"
    else:
        return f"{minutes}:{seconds:02d}.{centis:02d}"

# event popularity by year: for each event, in the given year, show the number
# of unique people who completed in that event and what percentage that is of the
# total people who competed in that same year.
def eventPopularityByYear(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    year = options[0]
    competitorsYear = set()
    competitorsByEvent = defaultdict(lambda: set())


    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter='\t')
        _ = next(reader) # junk the header row
        for row in reader:
            try:
                if year in row[0]:
                    event = row[1]
                    person = row[7]
                    competitorsByEvent[event].add(person)
                    competitorsYear.add(person)
            except:
                pass


    numCompetitors = len(competitorsYear)
    print(f"Found {numCompetitors} total {year} competitors:")
    popularityList = []
    for event in competitorsByEvent:
        popularityList.append( [event,len(competitorsByEvent[event]),len(competitorsByEvent[event])/numCompetitors] )
    popularityList.sort(key=lambda t: t[2], reverse=True)
    print("event\tcompetitors\tpercentage")
    for tup in popularityList:
        print(f"{tup[0]}\t{tup[1]}\t{tup[2]:.2%}")


# Like the previous, but for all years.
def eventPopularityAllTime(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    competitorsByEvent = defaultdict(lambda: set())
    allUniqueCompetitors = set()


    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter='\t')
        _ = next(reader) # junk the header row
        for row in reader:
            try:
                event = row[1]
                person = row[7]
                competitorsByEvent[event].add(person)
                allUniqueCompetitors.add(person)
            except:
                pass


    popularityList = []
    numCompetitors = len(allUniqueCompetitors)  
    print(f"Found {numCompetitors} unique competitors in WCA history.")
    for event in competitorsByEvent:
        popularityList.append( [event,len(competitorsByEvent[event]),len(competitorsByEvent[event])/numCompetitors] )
    popularityList.sort(key=lambda t: t[2], reverse=True)
    print("event\tcompetitors\tpercentage")
    for tup in popularityList:
        print(f"{tup[0]}\t{tup[1]}\t{tup[2]:.2%}")


# This stat looks at the number of comps individual people attend in the given year.
# That is, how many people only attended 1 comp all year? How many 2? 3? etc.
def compsAttendedHistogramByYear(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    year = options[0]
    competitorComps = defaultdict(lambda: set())


    # for every person, compile a set() of all comps they attended that year.
    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter='\t')
        _ = next(reader) # junk the header row
        for row in reader:
            if re.search(year, row[0]) is not None:
                comp = row[0]
                person = row[7]
                competitorComps[person].add(comp)


    # boil those sets down to a histogram
    compsAttended = defaultdict(lambda: 0)
    for person in competitorComps:
        num = len(competitorComps[person])
        compsAttended[num] += 1
    # See what the largest amount is:
    maxAttended = 0
    for num in compsAttended:
        if num > maxAttended:
            maxAttended = num
    print("Num attended:\tPeople")
    for num in range(1,maxAttended+1):
        print(f"{num}\t{compsAttended[num]}")


# for each event, find the first year in which it was held officially.
def yearAddedPerEvent(dump, options):
    targetFile = dump + "WCA_export_Competitions.tsv"
    yearAdded = defaultdict(lambda: 9999) # a value greater than any actual year.
    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter='\t')
        _ = next(reader) # junk the header row
        for row in reader:
            year = int(row[16]) # the comp
            eventSpecs = row[13]
            for e in eventSpecs.split():
                if year < yearAdded[e]:
                    yearAdded[e] = year
    # Boil that down to a more nicely-sorted list
    yearlist = []
    for e in yearAdded.keys():
        yearlist.append( (e,yearAdded[e]) )
    yearlist.sort(key=lambda t: t[1])
    print("event\tyear")
    for t in yearlist:
        print(f"{t[0]}\t{t[1]}")


# How many people represent each country, both by number and by percentage of total
def peoplePerCountry(dump, options):
    targetFile = dump + "WCA_export_Persons.tsv"
    countryCounts = defaultdict(lambda:0)
    totalPeople = 0
    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter="\t")
        _ = next(reader)
        for row in reader:
            country = row[2]
            countryCounts[country] += 1
            totalPeople += 1
    countryList = []
    for c in countryCounts.keys():
        countryList.append( (c, countryCounts[c], countryCounts[c]/totalPeople) )
    countryList.sort(key=lambda c: c[1], reverse=True)
    print("Country\tPeople")
    for c in countryList:
        print(f"{c[0]}\t{c[1]}\t{c[2]:.2%}")


# For a given competition, get the list of people who were first-time competitors
# at that comp.
def firstTimeCompetitorsByComp(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    compName = "".join(options) # this should work regardless of whether the user does or doesn't quote the comp name on the command line

    # First, make a set() of all people who were at that comp. That's one pass through targetFile.
    peopleAtTargetComp = set()
    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter="\t")
        _ = next(reader)
        for row in reader:
            if row[0] == compName:
                peopleAtTargetComp.add(row[7])

    # Second, build and cache a table of comp IDs and their dates.
    compIDsDates = {}
    with open(dump+"WCA_export_Competitions.tsv", "r", encoding="utf-8") as allComps:
        reader = csv.reader(allComps, delimiter="\t")
        _ = next(reader)
        for row in reader:
            compIDsDates[row[0]] = f"{row[16]}-{int(row[17]):02d}-{int(row[18]):02d}"

    # Third, go through targetFile again and for each record, if the record belongs
    # to one of our competitors, add a (CompID, date) tuple to a list for that person
    personComps = defaultdict(lambda: [])
    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter="\t")
        _ = next(reader)
        for row in reader:
            if row[7] in peopleAtTargetComp:
                tup = (row[0], compIDsDates[row[0]])
                if tup not in personComps[row[7]]:
                    personComps[row[7]].append(tup)
   
    # For each person's list of tuples, sort by the date, and if compName is the
    # first one, then print the person's ID. Or if we're feeling friendly, make a nice table
    # of IDs, names, and how many comps they've been to since.
    print(f"First time competitors at {compName}:")
    for id in peopleAtTargetComp:
        compList = personComps[id]
        compList.sort(key=lambda c: c[1])
        if compList[0][0] == compName:
            print(f"\t{id}, who has now been to {len(compList)} comps")

# For a given competition, get the list of people who were first-time competitors
# at that comp.
def slowestResultsByEvent(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    targetEvent = options[0]
    worstEver = 0
    worstSolver = None
    worstComp = None
    tenWorst = []
    fWorst = 0 # fastest worst times.

    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter="\t")
        _ = next(reader)
        for row in reader:
            if row[1] == targetEvent:
                personId = row[7]
                formatId = row[8]
                firstScoreCol = 9
                numResults = 5 # excessive. There are always 5 results, though some may be zeroes for non-average rounds
                slowest = max([ int(x) for x in row[firstScoreCol:firstScoreCol+numResults] ])
                for result in [ int(x) for x in row[firstScoreCol:firstScoreCol+numResults] ]:
                    if result >= fWorst: # then it could be one of the ten slowest
                        tenWorst.append( (result, personId, row[0]) )
                        tenWorst.sort(key=lambda t: t[0])
                        if len(tenWorst) > 10: # if we've exceeded 10, toss the fastest one
                            tenWorst = tenWorst[1:]
                        fWorst = tenWorst[0][0] # and get the new fastest worst time.
    print(f"The 10 slowest {targetEvent} results are:")
    for tup in tenWorst:
        print(f"  {resultToTimeStr(tup[0])} by {tup[1]} at {tup[2]}")

def numCompetitorsByEvent(dump, options):
    targetFile = dump + "WCA_export_Results.tsv"
    eventCounts = defaultdict(lambda: set())

    with open(targetFile, "r", encoding="utf-8") as target:
        reader = csv.reader(target, delimiter="\t")
        _ = next(reader)
        for row in reader:
            event    = row[1]
            personId = row[7]
            eventCounts[event].add(personId)

    print("Number of competitors for each event:")
    for event in eventCounts.keys():
        print(f"{event}: {len(eventCounts[event])}")

def usage():
    print("""Usage:
    wca_db_stats.py --list
          --or--
    wca_db_stats.py --dump/-d <directory> --stat/-s <stat name> [args]
          where:
          • <directory> points to an directory containing the unpacked .tsv version
            of a WCA database export from https://www.worldcubeassociation.org/export/results
          • <stat name> is one of the short strings listed below
          • [args] are any additional arguments required by that stat.""")
    print()
    print("""Available stats and their arguments
First Time Competitors by Comp
    name:   'ftcbc'
    args:    The WCA competition ID
    purpose: You give a WCA competition ID, like "UCSDWinter2020", and it generates
             a table of all the first-time competitors at that comp, and how many
             comps they have been to as of the time of the database dump.
Event Popularity by Year
    name:   'epby'
    args:    A 4-digit year
    purpose: Shows a table of WCA events and how many unique people competed in each
             one during the year you indicated.
Event Popularity All Time
    name:   'epat'
    args:    None
    purpose: Shows a table of WCA events and how many unique people have ever competed
             in each one.
Comps Attended Histogram By Year
    name:   'cahby'
    args:    A 4-digit year
    purpose: This stat looks at how many comps people attend in a given year, by
             showing you how many people went to 1, 2, 3, etc., comps.
Year Added Per Event (what year each event was first held in a WCA comp)
    name:   'yape'
    args:    None
    purpose: Shows a table of each WCA event and the first year it was held.
People by Country
    name:   'pbc'
    args:    None
    purpose: Shows a list of countries and how many competitors represent each one,
             both by number and percentage.
Slowest Results by Event
    name:    'srbe'
    args:    an event id, like '333' or '333bf'
    purpose: Shows a table of the slowest 10 results, with WCA ids, for a given event.
Number of Competitors by Event
    name:   ncbe
    args:   None
    purpose: counts the number of unique competitor IDs for each event, across WCA history.""")


# would prefer to use match/case, but can't count on everybody having python3.10 yet
callTable = {
    'ftcbc': firstTimeCompetitorsByComp,
    'epby':  eventPopularityByYear,
    'epat':  eventPopularityAllTime,
    'cahby': compsAttendedHistogramByYear,
    'yape':  yearAddedPerEvent,
    'ppc':   peoplePerCountry,
    'srbe':  slowestResultsByEvent,
    'ncbe':  numCompetitorsByEvent
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", "-d", help="relative path to directory containing an unpacked WCA database dump.")
    parser.add_argument("-s", "--stat", help="name of the stat you want to run")
    parser.add_argument("-l", "--list", default=False, action="store_true", help="Show help and list available stats and exit")
    args, options = parser.parse_known_args()
    if args.list:
        usage()
        exit()
    else:
        if args.dump is None or args.stat is None:
            print("Error: missing --dump and/or --stat argument")
            usage()
            exit()
        try:
            statFunc = callTable[args.stat] # this might throw if user put in garbage
            statFunc(args.dump, options)    # call the indicated function
        except:
            print(f"Error: unknown stat code: {args.stat} Available stat codes:")
            for key in callTable:
                print(f"    {key}")
