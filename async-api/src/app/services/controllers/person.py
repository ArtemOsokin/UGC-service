from app.api.v1.api_schemas import Params
from app.models.persons import ESPerson
from app.services.controllers.base import BaseService


class PersonService(BaseService):
    index = 'persons'
    model = ESPerson

    def get_cache_key(self, params: Params):
        args = [
            self.index,
            params.query,
            params.sort_field,
            params.pagination.offset,
            params.pagination.limit,
            params.filter_query.actors,
        ]
        print(args)
        return ':::'.join(str(i) for i in args)
