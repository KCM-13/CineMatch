from django.db import models

class Review(models.Model):
    movie_id = models.IntegerField()  # TMDb 영화 ID
    username = models.CharField(max_length=100)  # 리뷰 작성자 이름
    text = models.TextField()  # 리뷰 내용
    rating = models.IntegerField()  # 별점 (1~5)
    created_at = models.DateTimeField(auto_now_add=True)  # 작성 시간

    def __str__(self):
        return f"{self.username} - {self.movie_id}"
