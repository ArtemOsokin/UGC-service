from elasticsearch_dsl import Search

from app.api.v1.api_schemas import Params
from app.services.body_builder.abstract import SearchBodyBuilder


class BaseElasticBodyBuilder(SearchBodyBuilder):
    async def build_request_body(self, params: Params, index: str) -> dict:
        body = Search(index=index).sort(params.sort_field)
        if params.query:
            body = body.query('query_string', query=params.query)
        if params.is_subscriber is False:
            body = body.filter('term', subscription_required='false')
        return body.to_dict()
