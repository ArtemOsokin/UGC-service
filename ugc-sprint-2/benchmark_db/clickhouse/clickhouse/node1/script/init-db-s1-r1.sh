#!/bin/bash
set -e

clickhouse client -n <<-EOSQL

   CREATE DATABASE IF NOT EXISTS ugc_movies ON CLUSTER 'ugc_service_cluster';


  CREATE TABLE IF NOT EXISTS ugc_movies.films_bookmarks ON CLUSTER 'ugc_service_cluster'(
      user_id UUID CODEC(ZSTD(15)),
      film_id UUID CODEC(ZSTD(15)),
      created_at DateTime CODEC(DoubleDelta)
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_bookmarks', '{replica}')
    PARTITION BY toYYYYMMDD(created_at)
    ORDER BY user_id;


  CREATE TABLE IF NOT EXISTS default.films_bookmarks ON CLUSTER 'ugc_service_cluster'(
      user_id UUID CODEC(ZSTD(15)),
      film_id UUID CODEC(ZSTD(15)),
      created_at DateTime CODEC(DoubleDelta)
    ) ENGINE = Distributed('ugc_service_cluster', ugc_movies, films_bookmarks, rand());


  CREATE TABLE IF NOT EXISTS ugc_movies.films_likes ON CLUSTER 'ugc_service_cluster' (
      user_id UUID CODEC(ZSTD(15)),
      film_id UUID CODEC(ZSTD(15)),
      user_rating Float32 CODEC(LZ4HC),
      is_like UInt8 CODEC(LZ4HC),
      is_dislike UInt8 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_likes', '{replica}')
    PARTITION BY toYYYYMMDD(created_at)
    ORDER BY (film_id, user_id, is_like);


  CREATE TABLE IF NOT EXISTS default.films_likes ON CLUSTER 'ugc_service_cluster' (
      user_id UUID CODEC(ZSTD(15)),
      film_id UUID CODEC(ZSTD(15)),
      user_rating Float32 CODEC(LZ4HC),
      is_like UInt8 CODEC(LZ4HC),
      is_dislike UInt8 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
      ) ENGINE = Distributed('ugc_service_cluster', ugc_movies, films_likes, rand());


  CREATE TABLE IF NOT EXISTS ugc_movies.films_reviews ON CLUSTER 'ugc_service_cluster' (
      review_id UInt32 CODEC(LZ4HC),
      film_id UUID CODEC(ZSTD(15)),
      author String CODEC(ZSTD(15)),
      text_review String CODEC(ZSTD(15)),
      film_review_rating Float32 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_reviews', '{replica}')
    PARTITION BY toYYYYMMDD(created_at)
    ORDER BY (film_id, author);


  CREATE TABLE IF NOT EXISTS default.films_reviews ON CLUSTER 'ugc_service_cluster' (
      review_id UInt32 CODEC(LZ4HC),
      film_id UUID CODEC(ZSTD(15)),
      author String CODEC(ZSTD(15)),
      text_review String CODEC(ZSTD(15)),
      film_review_rating Float32 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
      ) ENGINE = Distributed('ugc_service_cluster', ugc_movies, films_reviews, rand());


  CREATE TABLE IF NOT EXISTS ugc_movies.review_likes ON CLUSTER 'ugc_service_cluster' (
      review_id UInt32 CODEC(LZ4HC),
      user_id UUID CODEC(ZSTD(15)),
      is_like UInt8 CODEC(LZ4HC),
      is_dislike UInt8 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/review_likes', '{replica}')
    PARTITION BY toYYYYMMDD(created_at)
    ORDER BY (review_id, is_like, is_dislike);


  CREATE TABLE IF NOT EXISTS default.review_likes ON CLUSTER 'ugc_service_cluster' (
      review_id UInt32 CODEC(LZ4HC),
      user_id UUID CODEC(ZSTD(15)),
      is_like UInt8 CODEC(LZ4HC),
      is_dislike UInt8 CODEC(LZ4HC),
      created_at DateTime CODEC(DoubleDelta)
      ) ENGINE = Distributed('ugc_service_cluster', ugc_movies, review_likes, intHash64(review_id));


EOSQL
