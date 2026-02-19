from django.shortcuts import render, redirect, get_object_or_404  # pyright: ignore[reportMissingImports]
from django.urls import reverse, reverse_lazy  # pyright: ignore[reportMissingImports]
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView # pyright: ignore[reportMissingImports]
from django.contrib.auth.mixins import LoginRequiredMixin  # pyright: ignore[reportMissingImports]
from django.db.models import Q  # pyright: ignore[reportMissingImports]
from .models import Diary, Comment


# Create your views here.
class DiaryListView(LoginRequiredMixin, ListView):
    template_name = 'diary/diary_list.html'
    model = Diary

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        queryset = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context

class DiaryDetailView(DetailView):
    template_name = 'diary/diary_detail.html'
    model = Diary

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Diary.objects.filter(Q(is_public=True) | Q(user=self.request.user))
        return Diary.objects.filter(is_public=True)

class DiaryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'diary/diary_create.html'
    model = Diary
    fields = ['title', 'content', 'is_public']
    success_url = reverse_lazy('diary-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DiaryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'diary/diary_update.html'
    model = Diary
    fields = ['title', 'content', 'is_public']

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('diary-detail', kwargs={'pk': self.object.pk})

class DiaryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'diary/diary_delete.html'
    model = Diary
    success_url = reverse_lazy('diary-list') 

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)

def index_view(request):
    diary_list = Diary.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'diary/index.html', {'diary_list': diary_list})

class CreateCommentView(LoginRequiredMixin, CreateView):
    template_name = 'diary/comment_form.html'
    model = Comment
    fields = ['text']
    success_url = reverse_lazy('diary-detail')

    def dispatch(self, request, *args, **kwargs):
        self.diary = get_object_or_404(
            Diary,
            Q(is_public=True) | Q(user=request.user),
            pk=kwargs.get('pk'),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diary'] = self.diary
        return context


    def form_valid(self, form):
        form.instance.diary = self.diary
        form.instance.user = self.request.user
        return super().form_valid(form)



    def get_success_url(self):
        return reverse('diary-detail', kwargs={'pk': self.object.diary.pk})
