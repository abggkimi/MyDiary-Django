from django.urls import path  # pyright: ignore[reportMissingImports]

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('diary/', views.DiaryListView.as_view(), name='diary-list'),
    path('diary/<int:pk>/', views.DiaryDetailView.as_view(), name='diary-detail'),
    path('diary/create/', views.DiaryCreateView.as_view(), name='diary-create'),
    path('diary/update/<int:pk>/', views.DiaryUpdateView.as_view(), name='diary-update'),
    path('diary/delete/<int:pk>/', views.DiaryDeleteView.as_view(), name='diary-delete'),
    path('diary/comment/<int:pk>/', views.CreateCommentView.as_view(), name='comment'),
]