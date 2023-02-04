from pydantic import BaseModel


class CacheObj(BaseModel):
    key_name: str
    key_value: str


class CacheKey:
    _separator: str = '::'

    def _create_cache_key(self,
                          values: list[CacheObj]) -> str:
        key = f'{self.index}{self._separator}'
        for value in values:
            key += f'{value.key_name}{self._separator}{value.key_value},'

        return key
