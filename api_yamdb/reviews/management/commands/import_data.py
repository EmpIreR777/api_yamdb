import csv
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    FILE_PATH = Path(settings.BASE_DIR) / 'static' / 'data'

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(self.FILE_PATH / csv_f, mode='r',
                      encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                objs = []
                for data in reader:
                    if model.objects.filter(id=data['id']).exists():
                        continue
                    objs.append(model(**data))
                model.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS('Data successfully imported'))
