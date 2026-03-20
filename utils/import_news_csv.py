import csv
from datetime import datetime

from django.db import transaction

from kyykka.models import News


def old_news():

    with open("new_nkl_news.csv", encoding="utf-8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=";", escapechar='"')
        next(readCSV)  # Skip header row
        with transaction.atomic():
            for row in readCSV:
                title = row[0]
                author = row[1]
                date = row[2]
                time = row[3]
                article = row[4]

                datetime_str = f"{date} {time}"
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                News.objects.create(
                    header=title, writer=author, date=datetime_obj, text=article
                )
