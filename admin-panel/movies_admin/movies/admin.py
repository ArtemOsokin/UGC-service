from django.contrib import admin
from .models import Filmwork, FilmworkPerson, FilmworkGenre, Genre, Person


class PersonRoleInline(admin.TabularInline):
    model = FilmworkPerson
    extra = 0


class GanreFilmInline(admin.TabularInline):
    model = FilmworkGenre
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating',)
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating', 'subscription_required'
    )
    list_per_page = 20
    sortable_by = ('title', 'creation_date',)
    search_fields = ('title', 'description',)
    inlines = [
        PersonRoleInline, GanreFilmInline
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date',)
    list_per_page = 20
    search_fields = ('full_name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    list_per_page = 20
