from app.api.v1.api_schemas import Params
from app.models.films import ESFilmwork
from app.services.controllers.base import BaseService


class FilmService(BaseService):
    index = 'movies'
    model = ESFilmwork

    def get_cache_key(self, params: Params):
        args = [
            self.index,
            params.query,
            params.sort_field,
            params.pagination.offset,
            params.pagination.limit,
            params.filter_query.genre,
        ]

        return ':::'.join(str(i) for i in args)
