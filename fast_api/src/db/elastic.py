import abc
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError


class AsyncDataProvider(abc.ABC):
    """
    Абстрактная прослойка для методов
    """

    @abc.abstractmethod
    async def search(
            self,
            index: str,
            query: str,
            page_size: int,
            page_number: int,
    ):
        pass

    @abc.abstractmethod
    async def get_all(
            self,
            index: str,
            sort: str,
            filter_name: str,
            filter_arg: str,
            page_size: int,
            page_number: int,
    ):
        pass

    @abc.abstractmethod
    async def get_by_id(self, index: str, id: str) -> Optional[dict]:
        pass


class AsyncElasticProvider(AsyncDataProvider):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search(
            self,
            index: str,
            query: str,
            page_size: int,
            page_number: int,
    ) -> list[dict]:
        """
        Поиск результата по запросу
        """
        body = {"query": {"multi_match": {"query": query, "fuzziness": "auto"}}}
        return await self._search(index, body, page_size, page_number)

    async def get_by_id(
            self,
            index: str,
            id: str,
    ) -> Optional[dict]:
        """
        Здесь мы получаем информацию только о одном элементе по айди из эластики.
        """
        try:
            doc = await self.elastic.get(index, id)
        except NotFoundError:
            return None
        return doc['_source']

    async def get_all(
            self,
            index: str,
            sort: str,
            filter_name: str,
            filter_arg: str,
            page_size: int,
            page_number: int,
    ):
        """
        Здесь мы получаем информацию только о нескольких элементах из эластики.
        """

        body = {"query": {"bool": {"must": {"match_all": {}}}}}

        if sort:
            body["sort"] = [{f"{sort}": "desc"}, "_score"]

        if filter_name and filter_arg:
            body["query"]["bool"]["filter"] = {
                "match": {
                    f"{filter_name}": f"{filter_arg}"
                }
            }

        return await self._search(index, body, page_size, page_number)

    async def _search(
            self,
            index: str,
            body: dict,
            page_size: int,
            page_number: int,
    ) -> list[dict]:
        """
        Вспомогательное решение для поиска. Поскольку используется дважды.
        """

        response = await self.elastic.search(
            index=index,
            body=body,
            from_=(page_number - 1) * page_size,
            size=page_size,
        )
        return [d["_source"] for d in response["hits"]["hits"]]


es: Optional[AsyncDataProvider] = None


async def get_elastic() -> AsyncDataProvider:
    return es
