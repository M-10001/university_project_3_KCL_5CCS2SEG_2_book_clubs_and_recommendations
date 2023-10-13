import os
import csv
import sys
import re

from surprise import Dataset
from surprise import Reader

from collections import defaultdict
import numpy as np
import pandas as pd

class DataHandler:

    bookID_to_name = {}
    name_to_bookID = {}
    ratingsPath = 'book-review-dataset/BX-Book-Ratings.csv'
    booksPath = 'book-review-dataset/BX_Books.csv'

    def loadData(self, every_nth):

        # Look for files relative to the directory we are running from
        os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.bookID_to_name = {}
        self.name_to_bookID = {}
        self.every_nth = every_nth
        self.doAllRatings = False

        with open(self.booksPath, newline='', encoding='Windows-1252') as csvfile:
                bookReader = csv.reader(csvfile, delimiter = ';', quoting = csv.QUOTE_ALL)
                next(bookReader)

                for row in bookReader:
                    bookID = row[0]
                    bookName = row[1]
                    self.bookID_to_name[bookID] = bookName
                    self.name_to_bookID[bookName] = bookID

        if (self.every_nth <= 0):
            self.doAllRatings = True

        ratings_dict = {
            'userID' : [],
            'itemID' : [],
            'rating' : []
        }

        total_ratings_loaded = 0

        with open(self.ratingsPath, newline = '', encoding = 'Windows-1252') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ';', quoting = csv.QUOTE_ALL)
            next(csv_reader)
            i = 0

            for row in csv_reader:
                i = i + 1

                if ((self.doAllRatings or (i >= self.every_nth)) and (row[1] in self.bookID_to_name)):
                    ratings_dict['userID'].append(int(row[0]))
                    ratings_dict['itemID'].append(row[1])
                    ratings_dict['rating'].append(int(row[2]))
                    total_ratings_loaded = total_ratings_loaded + 1
                    i = 0



        df = pd.DataFrame(ratings_dict)

        reader = Reader(rating_scale = (0, 10))

        ratingsDataset = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader = reader)

        print("Total ratings loaded: " + str(total_ratings_loaded))

        return ratingsDataset

    def getUserRatings(self, user):
        userRatings = []
        hitUser = False

        with open(self.ratingsPath, newline='', encoding='Windows-1252') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';', quoting = csv.QUOTE_ALL)
            next(ratingReader)
            i = 0

            for row in ratingReader:
                i = i + 1
                userID = int(row[0])

                if ((self.doAllRatings or (i >= self.every_nth)) and (row[1] in self.bookID_to_name)):
                    if (user == userID):
                        bookID = row[1]
                        rating = float(row[2])
                        userRatings.append((bookID, rating))
                        hitUser = True

                    if (hitUser and (user != userID)):
                        break

                    i = 0

        return userRatings

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)

        with open(self.ratingsPath, newline='', encoding = 'Windows-1252') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';', quoting = csv.QUOTE_ALL)
            next(ratingReader)
            i = 0

            for row in ratingReader:
                i = i + 1

                if ((self.doAllRatings or (i >= self.every_nth)) and (row[1] in self.bookID_to_name)):
                    bookID = row[1]
                    ratings[bookID] += 1
                    i = 0

        rank = 1

        for bookID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[bookID] = rank
            rank += 1

        return rankings

    # def getGenres(self):
    #     genres = defaultdict(list)
    #     genreIDs = {}
    #     maxGenreID = 0
    #     with open(self.moviesPath, newline='', encoding='ISO-8859-1') as csvfile:
    #         movieReader = csv.reader(csvfile)
    #         next(movieReader)  #Skip header line
    #         for row in movieReader:
    #             movieID = int(row[0])
    #             genreList = row[2].split('|')
    #             genreIDList = []
    #             for genre in genreList:
    #                 if genre in genreIDs:
    #                     genreID = genreIDs[genre]
    #                 else:
    #                     genreID = maxGenreID
    #                     genreIDs[genre] = genreID
    #                     maxGenreID += 1
    #                 genreIDList.append(genreID)
    #             genres[movieID] = genreIDList
    #     # Convert integer-encoded genre lists to bitfields that we can treat as vectors
    #     for (movieID, genreIDList) in genres.items():
    #         bitfield = [0] * maxGenreID
    #         for genreID in genreIDList:
    #             bitfield[genreID] = 1
    #         genres[movieID] = bitfield
    #
    #     return genres

    # def getYears(self):
    #     p = re.compile(r"(?:\((\d{4})\))?\s*$")
    #     years = defaultdict(int)
    #     with open(self.moviesPath, newline='', encoding='ISO-8859-1') as csvfile:
    #         movieReader = csv.reader(csvfile)
    #         next(movieReader)
    #         for row in movieReader:
    #             movieID = int(row[0])
    #             title = row[1]
    #             m = p.search(title)
    #             year = m.group(1)
    #             if year:
    #                 years[movieID] = int(year)
    #     return years

    # def getMiseEnScene(self):
    #     mes = defaultdict(list)
    #     with open("LLVisualFeatures13K_Log.csv", newline='') as csvfile:
    #         mesReader = csv.reader(csvfile)
    #         next(mesReader)
    #         for row in mesReader:
    #             movieID = int(row[0])
    #             avgShotLength = float(row[1])
    #             meanColorVariance = float(row[2])
    #             stddevColorVariance = float(row[3])
    #             meanMotion = float(row[4])
    #             stddevMotion = float(row[5])
    #             meanLightingKey = float(row[6])
    #             numShots = float(row[7])
    #             mes[movieID] = [avgShotLength, meanColorVariance, stddevColorVariance,
    #                meanMotion, stddevMotion, meanLightingKey, numShots]
    #     return mes

    def getBookName(self, bookID):
        if bookID in self.bookID_to_name:
            return self.bookID_to_name[bookID]
        else:
            return ""

    def getBookID(self, bookName):
        if bookName in self.name_to_bookID:
            return self.name_to_bookID[bookName]
        else:
            return 0
