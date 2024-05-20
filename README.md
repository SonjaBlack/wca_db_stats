# wca_db_stats.py

Python script to generate miscellaneous stats that were of interest to the author.

# Usage:

1. Have python 3.6 or later installed
2. Download the latest [WCA database export](https://www.worldcubeassociation.org/export/results). Note, you must get the .tsv version of the database, not the .sql version
3. Unpack the database export into some convenient directory.
4. Clone this repo to your computer, or just download the individual `wca_db_stats.py` file from here on Github.
5. From your command line, invoke this script with the location of your database export, the name of one of the supported stats, and any other parameters required by that stat.

For example, presuming that this script is in your current directory, and you have unpacked the database export to ~/WCA_db:

```
python wca_db_stats.py --dump ~/WCA_db/ --stat cahby 2023
```

will generate for you a Competitions Attended Histogram by Year report for 2023.

# Supported Stats

## First Time Competitors by Competition

`--stat ftcbc <comp ID>`

You provide the WCA ID of any comp, and it will generate for you a list of all the people who were first-timers at that comp. As well, it tells you how many comps those people have gone on to particpate in.

## Event Popularity by Year

`--stat epby <year>`

You provide a year, and it shows you a table of how many unique people competed in each event during that year, sorted by popularity. No surprise, 3x3 always comes out on top.

## Event Popularity All Time

`--stat epat`

Same as Event Popularity by Year, but for all years together.

## Competitions Attended Histogram by Year

`--stat cahby <year>`

You provide a year, and it generates for you a histogram of number of competitors who have attended different amounts of comps during the year. That is, how many people only went to 1 comp, 2 comps, ... up through whatever the largest number is for the year. Fun fact: in 2023, some wildly dedicated cuber went to 85 comps!

## Year Added Per Event

`--stat yape`

Shows a simple table of what year each event was first held at competition recognized by the WCA.

## People Per Country

`--stat ppc`

Shows a simple table of how many people are registered to represent each country, both by the raw number and by percentage.

Fun fact: as of this writing, Monaco, Haiti, Togo, Guyana, Democratic Republic of the Congo, Grenada, Somalia, Maldives, Fiji, Laos, Cameroon, and Saint Lucia are all represented by just one lonely cuber each. Time to hold some competitions in the Caribbean, I think!

# Contributions

If you somehow think this hacky little tool is worth your time to add some additional stats, I've tried to make that easy:

1. Add a new stat-generating function. Use the existing ones as a template. You'll see they all have the same call signature and very similar structures. Please follow the same naming convention I've used, which is that the stat names have the general form:

```
thing it computes + "by" or "per" + what the thing is relative to 
```

If a stat is "by" something, then users should be expected to provide some sort of parameter(s) to the computation, such as a year or a competition name or a WCA ID or whatever you want, really. Those parameters will be available to your function as elements of the `options` list passed to your function.

2. Register a new short-name for your function in the `callTable` dictionary near the bottom of the script. 

3. Add documentation for your new function to this file and to the `usage()` function.

4. Submit a pull request.
