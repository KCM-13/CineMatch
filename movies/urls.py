from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('popular/', views.popular_movies, name='popular_movies'),
    path('search/', views.search_movies, name='search_movies'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),  # 영화 상세 페이지
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'), #리뷰 남기기
    path('recommend/', views.recommend_movies, name='recommend_movies'), #영화 추천
    path('search-by-genre/', views.search_by_genre, name='search_by_genre'),  # 장르 입력 페이지
    path('search-by-genre/results/', views.genre_results, name='genre_results'),  # 장르 결과 페이지
    path('search-by-actor/', views.search_by_actor, name='search_by_actor'),  # 배우 검색 입력
    path('search-by-actor/results/', views.actor_results, name='actor_results'),  # 배우 검색 결과
    path('top-rated-movies/', views.top_rated_movies, name='top_rated_movies'),  # 평점 높은 영화
]
