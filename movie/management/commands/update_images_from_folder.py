import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        images_folder = 'media/movie/images/'
        movies = Movie.objects.all()
        for movie in movies:
            for filename in os.listdir(images_folder):
                name, ext = os.path.splitext(filename)
                if name == f"m_{movie.title}":
                    movie.image = os.path.join('movie/images', filename)
                    movie.save()
                    break