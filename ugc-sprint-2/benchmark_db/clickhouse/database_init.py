from benchmark_db.clickhouse.settings import settings
from clickhouse_driver import connect

conn = connect(
    host=settings.CH.HOSTS[0],
    port=settings.CH.PORT,
    user=settings.CH.USER,
    password=settings.CH.PASSWORD,
    ca_certs=settings.CH.CACERT,
    secure=True,
)

cursor = conn.cursor()


def initialize_database():
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS ugc_movies ON CLUSTER 'c9qqqv4tsti7miv2uhfi'"
    )

    cursor.execute(
        """
                  CREATE TABLE IF NOT EXISTS ugc_movies.films_bookmarks ON CLUSTER 'c9qqqv4tsti7miv2uhfi'(
                      user_id UUID CODEC(ZSTD(15)),
                      film_id UUID CODEC(ZSTD(15)),
                      created_at DateTime CODEC(DoubleDelta)
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_bookmarks', '{replica}')
                    PARTITION BY toYYYYMMDD(created_at)
                    ORDER BY user_id;
                """
    )

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS default.films_bookmarks ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          user_id UUID CODEC(ZSTD(15)),
          film_id UUID CODEC(ZSTD(15)),
          created_at DateTime CODEC(DoubleDelta)
        ) ENGINE = Distributed('c9qqqv4tsti7miv2uhfi', ugc_movies, films_bookmarks, rand());
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS ugc_movies.films_likes ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          user_id UUID CODEC(ZSTD(15)),
          film_id UUID CODEC(ZSTD(15)),
          user_rating Float32 CODEC(LZ4HC),
          is_like UInt8 CODEC(LZ4HC),
          is_dislike UInt8 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
        ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_likes', '{replica}')
        PARTITION BY toYYYYMMDD(created_at)
        ORDER BY (film_id, user_id, is_like);
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS default.films_likes ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          user_id UUID CODEC(ZSTD(15)),
          film_id UUID CODEC(ZSTD(15)),
          user_rating Float32 CODEC(LZ4HC),
          is_like UInt8 CODEC(LZ4HC),
          is_dislike UInt8 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
          ) ENGINE = Distributed('c9qqqv4tsti7miv2uhfi', ugc_movies, films_likes, rand());
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS ugc_movies.films_reviews ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          review_id UInt32 CODEC(LZ4HC),
          film_id UUID CODEC(ZSTD(15)),
          author String CODEC(ZSTD(15)),
          text_review String CODEC(ZSTD(15)),
          film_review_rating Float32 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
        ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_reviews', '{replica}')
        PARTITION BY toYYYYMMDD(created_at)
        ORDER BY (film_id, author);
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS default.films_reviews ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          review_id UInt32 CODEC(LZ4HC),
          film_id UUID CODEC(ZSTD(15)),
          author String CODEC(ZSTD(15)),
          text_review String CODEC(ZSTD(15)),
          film_review_rating Float32 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
          ) ENGINE = Distributed('c9qqqv4tsti7miv2uhfi', ugc_movies, films_reviews, rand());
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS ugc_movies.review_likes ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          review_id UInt32 CODEC(LZ4HC),
          user_id UUID CODEC(ZSTD(15)),
          is_like UInt8 CODEC(LZ4HC),
          is_dislike UInt8 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
        ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/review_likes', '{replica}')
        PARTITION BY toYYYYMMDD(created_at)
        ORDER BY (review_id, is_like);
    """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS default.review_likes ON CLUSTER 'c9qqqv4tsti7miv2uhfi' (
          review_id UInt32 CODEC(LZ4HC),
          user_id UUID CODEC(ZSTD(15)),
          is_like UInt8 CODEC(LZ4HC),
          is_dislike UInt8 CODEC(LZ4HC),
          created_at DateTime CODEC(DoubleDelta)
          ) ENGINE = Distributed('c9qqqv4tsti7miv2uhfi', ugc_movies, review_likes, intHash64(review_id));
    """
    )


conn.close()
