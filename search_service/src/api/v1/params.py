from fastapi import Query
from src.core.config import settings


class PaginatedParams:
    """
    Параметры для пагинации.
    """
    def __init__(
            self,
            page_size: int = Query(
                settings.default_page_size,
                alias='page[size]',
                description='Размер страницы.',
                ge=1
            ),
            page_number: int = Query(
                settings.default_page_number,
                alias='page[number]',
                description='Номер страницы.',
                ge=1
            )
    ):
        self.page_size = page_size
        self.page_number = page_number