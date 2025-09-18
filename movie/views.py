from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv


def home(request):
    searchTerm = request.GET.get('searchMovie', '')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})


def about(request):
    return render(request, 'about.html', {'name': 'Laura Indabur G'})   


def recommendation (request):
    return render(request, 'recomendation.html')


def statistics_view(request):
    matplotlib.use('Agg')
    # Obtener todas las películas
    all_movies = Movie.objects.all()
    # Crear un diccionario para almacenar la cantidad de películas por género
    movie_counts_by_genre = {}
    # Filtrar las películas por año y contar la cantidad de películas por año
    for movie in all_movies:
        primer_genero = movie.genre.split(',')[0].strip() if movie.genre else "None"  # primer genero es partiendo la cadena por comas y tomando el primer elemento
        if primer_genero in movie_counts_by_genre:
            movie_counts_by_genre[primer_genero] += 1   #si ya existe el genero, incrementa en 1
        else:
            movie_counts_by_genre[primer_genero] = 1  #si no está, lo agrega al diccionario y lo inicializa en 1
    # Ancho de las barras
    bar_width = 0.5
    # Posiciones de las barras
    bar_positions = range(len(movie_counts_by_genre))
    # Crear la gráfica de barras
    plt.bar(bar_positions, movie_counts_by_genre.values(), width=bar_width, align='center')
    # Personalizar la gráfica
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_genre.keys(), rotation=90)
    # Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)
    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    # Renderizar la plantilla statistics.html con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic})

def signup(request):
    email= request.GET.get('email')
    return render(request, 'signup.html', {'email': email})  #envia pasando un diccionario

#---------------------------------------------------------------------------------------------------------------------

load_dotenv('openai.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recommendation(request):
    recommended_movies = []
    prompt = ""

    if request.method == "POST":
        prompt = request.POST.get("prompt", "")
        if prompt:
            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
            similarities = []
            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                sim = cosine_similarity(prompt_emb, movie_emb)
                similarities.append((sim, movie))
            # Ordenar por similitud descendente y tomar los 3 primeros
            similarities.sort(reverse=True, key=lambda x: x[0])
            recommended_movies = similarities[:3]

    return render(request, "recomendation.html", {
        "recommended_movies": recommended_movies,
        "prompt": prompt
    })