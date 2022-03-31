from app.api.v1.api_schemas import Params
from app.models.genres import ESGenre
from app.services.controllers.base import BaseService


class GenreService(BaseService):
    index = 'genres'
    model = ESGenre

    def get_cache_key(self, params: Params):
        args = [self.index, params.pagination.offset, params.pagination.limit]
        return ':::'.join(str(i) for i in args)
