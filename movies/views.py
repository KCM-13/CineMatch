from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
import requests
from .models import Review
import random
from django.core.paginator import Paginator


def home(request):
    return render(request, 'movies/home.html')

def popular_movies(request):
    # TMDb API 호출
    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])  # 영화 목록

    # JSON 형식으로 응답 
    if request.GET.get('format') == 'json':
        return JsonResponse(data)

    # HTML 템플릿 렌더링
    return render(request, 'movies/popular_movies.html', {'movies': movies})

# 영화 검색 기능
def search_movies(request):
    query = request.GET.get('query')  # 검색어 가져오기
    if not query:
        return HttpResponse("검색어를 입력하세요.", status=400)

    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&language=ko-KR"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])  # 검색 결과 가져오기

    # HTML 템플릿 렌더링
    return render(request, 'movies/search_results.html', {'movies': movies, 'query': query})

# 영화 상세 정보
def movie_detail(request, movie_id):

    # TMDB API로 영화 정보 가져오기
    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR"
    response = requests.get(url)
    movie = response.json()

    # 세션에 최근 본 영화 저장
    if 'recent_movies' not in request.session:
        request.session['recent_movies'] = []
    if movie_id not in request.session['recent_movies']:
        request.session['recent_movies'].append(movie_id)
        request.session.modified = True

    # 영화에 대한 리뷰 가져오기, 정렬 처리
    reviews = Review.objects.filter(movie_id=movie_id)

    # 정렬 옵션 처리
    sort = request.GET.get('sort', 'latest')
    if sort == 'highest':
        reviews = reviews.order_by('-rating')  # 높은 평점순
    elif sort == 'lowest':
        reviews = reviews.order_by('rating')  # 낮은 평점순
    else:  # 기본값: 최신순
        reviews = reviews.order_by('-created_at')

    # 페이지네이션 처리
    paginator = Paginator(reviews, 4)  # 한 페이지에 4개 리뷰
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'movie': movie,
        'reviews': page_obj, 
        'sort': sort
    }

    return render(request, 'movies/movie_detail.html', context)

# 리뷰 작성 기능
def add_review(request, movie_id):
    if request.method == 'POST':
        username = request.POST.get('username', '익명')  # 기본값은 '익명'
        text = request.POST.get('text', '')
        rating = int(request.POST.get('rating', 5))  # 기본값은 5점
        
        # 리뷰 저장
        Review.objects.create(movie_id=movie_id, username=username, text=text, rating=rating)

        # 상세 페이지로 이동
        return redirect('movie_detail', movie_id=movie_id)


#장르 기반 추천
def search_by_genre(request):
    """
    장르 입력 페이지
    """
    return render(request, 'movies/search_by_genre.html')

def genre_results(request):
    """
    장르 기반 영화 추천
    """
    # 사용자 입력값 가져오기
    genre_name = request.GET.get('genre', '').strip()
    if not genre_name:
        return render(request, 'movies/genre_results.html', {'movies': [], 'message': '장르를 입력하세요.'})

    # TMDb API에서 장르 ID 가져오기
    api_key = settings.TMDB_API_KEY
    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=ko-KR"
    response = requests.get(genre_url)
    genres_data = response.json()
    genres = {g['name']: g['id'] for g in genres_data.get('genres', [])}

    # 입력된 장르가 유효한지 확인
    genre_id = genres.get(genre_name)
    if not genre_id:
        return render(request, 'movies/genre_results.html', {'movies': [], 'message': '유효하지 않은 장르입니다.'})

    # 해당 장르의 영화 검색
    movie_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}&language=ko-KR"
    response = requests.get(movie_url)
    movies_data = response.json().get('results', [])

    # 랜덤으로 10개 선택
    recommended_movies = random.sample(movies_data, min(10, len(movies_data)))

    return render(request, 'movies/genre_results.html', {'movies': recommended_movies, 'genre_name': genre_name})

#배우 기반 추천
def search_by_actor(request):
    """
    배우 검색 페이지
    """
    return render(request, 'movies/search_by_actor.html')

def actor_results(request):
    """
    배우 기반 영화 추천
    """
    # 사용자 입력값 가져오기
    actor_name = request.GET.get('actor', '').strip()
    if not actor_name:
        return render(request, 'movies/actor_results.html', {'movies': [], 'message': '배우 이름을 입력하세요.'})

    # TMDb API에서 배우 ID 검색
    api_key = settings.TMDB_API_KEY
    search_url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={actor_name}&language=ko-KR"
    response = requests.get(search_url)
    search_data = response.json()
    results = search_data.get('results', [])

    if not results:
        return render(request, 'movies/actor_results.html', {'movies': [], 'message': '해당 배우를 찾을 수 없습니다.'})

    # 첫 번째 검색 결과의 배우 ID 사용
    actor_id = results[0].get('id')
    actor_name = results[0].get('name')  # 배우 이름 가져오기

    # TMDb API에서 배우의 출연 영화 가져오기
    movies_url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={api_key}&language=ko-KR"
    response = requests.get(movies_url)
    movies_data = response.json().get('cast', [])  # 출연 영화 목록

    # 랜덤으로 10개 선택
    recommended_movies = random.sample(movies_data, min(10, len(movies_data)))

    return render(request, 'movies/actor_results.html', {'movies': recommended_movies, 'actor_name': actor_name})

# 최근 검색한 영화 기반 추천
def recommend_movies(request):
    api_key = settings.TMDB_API_KEY

    # 최근 본 영화 가져오기
    recent_movies = request.session.get('recent_movies', [])
    if not recent_movies:
        return render(request, 'movies/recommend_movies.html', {'movies': [], 'message': '최근 본 영화가 없습니다.'})

    # 최근 본 영화의 장르 수집
    genres = []
    for movie_id in recent_movies[-5:]:  # 최근 본 영화 5개
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR"
        response = requests.get(url)
        movie_data = response.json()
        genres.extend([genre['id'] for genre in movie_data.get('genres', [])])

    # 중복 제거 및 가장 많이 본 장르 추출
    genres = list(set(genres))

    # 추천 영화 검색
    recommended_movies = []
    for genre_id in genres:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}&language=ko-KR"
        response = requests.get(url)
        data = response.json()
        recommended_movies.extend(data.get('results', []))

    return render(request, 'movies/recommend_movies.html', {'movies': recommended_movies[:10]})

# 평점 높은 순으로 추천
def top_rated_movies(request):
    """
    평점 높은 영화 추천
    """
    api_key = settings.TMDB_API_KEY
    base_url = "https://api.themoviedb.org/3/movie/top_rated"
    
    # 1부터 10까지의 랜덤 페이지 선택
    random_page = random.randint(1, 10)
    url = f"{base_url}?api_key={api_key}&language=ko-KR&page={random_page}"
    
    response = requests.get(url)
    movies_data = response.json().get('results', [])

    # 랜덤으로 10개 선택
    recommended_movies = random.sample(movies_data, min(10, len(movies_data)))

    return render(request, 'movies/top_rated_movies.html', {'movies': recommended_movies})