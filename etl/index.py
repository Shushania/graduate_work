INDEXES = ['''
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "russian_stop": {
                "type":       "stop",
                "stopwords":  "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        },
        "char_filter":{
            "e_char_filter": {
                "type": "mapping",
                "mappings": ["Ё => Е", "ё => е", "Э => Е", "э => е"]
            }
        },
        "analyzer": {
            "ru": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_stemmer"
                ],
                "char_filter": ["e_char_filter"]      
            }
        }
    }
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "imdb_rating": {
        "type": "float"
      },
      "genre": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru",
        "fields": {
          "raw": { 
            "type":  "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru"
      },
      "director": {
        "type": "text",
        "analyzer": "ru"
      },
      "actors_names": {
        "type": "text",
        "analyzer": "ru"
      },
      "writers_names": {
        "type": "text",
        "analyzer": "ru"
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru"
          }
        }
      }
    }
  }
}
''', '''
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "russian_stop": {
                "type":       "stop",
                "stopwords":  "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        },
        "char_filter":{
            "e_char_filter": {
                "type": "mapping",
                "mappings": ["Ё => Е", "ё => е", "Э => Е", "э => е"]
            }
        },
        "analyzer": {
            "ru": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_stemmer"
                ],
                "char_filter": ["e_char_filter"]      
            }
        }
    }
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text",
        "analyzer": "ru",
        "fields": {
          "raw": { 
            "type":  "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru"
      }
    }
  }
}
''', '''
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "russian_stop": {
                "type":       "stop",
                "stopwords":  "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        },
        "char_filter":{
            "e_char_filter": {
                "type": "mapping",
                "mappings": ["Ё => Е", "ё => е", "Э => Е", "э => е"]
            }
        },
        "analyzer": {
            "ru": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_stemmer"
                ],
                "char_filter": ["e_char_filter"]      
            }
        }
    }
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "full_name": {
        "type": "text",
        "analyzer": "ru",
        "fields": {
          "raw": { 
            "type":  "keyword"
          }
        }
      }
    }
  }
}
''']