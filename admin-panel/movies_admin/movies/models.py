from typing_extensions import Required
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class TimeStampedIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedIDModel):
    name = models.CharField(_('наименование'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = "content\".\"genre"
        managed = True

    def __str__(self):
        return self.name


class Person(TimeStampedIDModel):
    full_name = models.CharField(_('Полное имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)

    class Meta:
        verbose_name = _('персона')
        verbose_name_plural = _('персоны')
        db_table = "content\".\"person"
        managed = True

    def __str__(self):
        return self.full_name


class RoleType(models.TextChoices):
    DIRECTOR = 'director', _('режисёр')
    ACTOR = 'actor', _('актёр')
    WRITER = 'writer', _('сценарист')


class FilmworkPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_('кинопроизведение'))
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('персона'))
    role = models.CharField(_('роль'), max_length=50, choices=RoleType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_role_person_film_work'),
        ]
        db_table = "content\".\"person_film_work"
        verbose_name = _('участник кинопроизведения')
        verbose_name_plural = _('участники кинопроизведения')
        managed = True


class FilmworkGenre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_('кинопроизведение'))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('жанр'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_genre_film_work'),
        ]
        db_table = "content\".\"genre_film_work"
        verbose_name = _('жанр кинопроизведения')
        verbose_name_plural = _('жанры кинопроизведения')
        managed = True


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('ТВ-шоу')


class Filmwork(TimeStampedIDModel):
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True, null=True)
    subscription_required = models.BooleanField(_('флаг необходимости наличия подписки'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True, null=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True, null=True)
    type = models.CharField(_('тип'), max_length=20, choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre, through='FilmworkGenre', verbose_name=_('жанры'))
    persons = models.ManyToManyField(Person, through='FilmworkPerson', verbose_name=_('персоны'))

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        db_table = "content\".\"film_work"
        managed = True

    def __str__(self):
        return self.title
