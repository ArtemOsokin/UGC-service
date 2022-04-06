#!/bin/bash
set -e

clickhouse client -n <<-EOSQL

  CREATE DATABASE IF NOT EXISTS shard;

  CREATE DATABASE IF NOT EXISTS replica;

  CREATE TABLE IF NOT EXISTS default.kafka_films_bookmarks (
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8
    ) ENGINE = Kafka SETTINGS kafka_broker_list = 'rc1b-dt0p7ntrbdum3iqb.mdb.yandexcloud.net:9091',
                              kafka_topic_list = 'films_bookmarks',
                              kafka_group_name = 'clickhouse',
                              kafka_format = 'JSONEachRow';

  CREATE TABLE IF NOT EXISTS shard.films_bookmarks(
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard1/films_bookmarks', 'replica_bookmarks_1')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS replica.films_bookmarks(
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard2/films_bookmarks', 'replica_bookmarks_2')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS default.films_bookmarks (
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
    ) ENGINE = Distributed('ugc_service_cluster', '', films_bookmarks, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_bookmarks_mv TO shard.films_bookmarks AS
      SELECT *, _timestamp as timestamp, _key as key, _topic as topic, _partition as partition
      FROM default.kafka_films_bookmarks;



  CREATE TABLE IF NOT EXISTS default.kafka_films_progress (
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8
    ) ENGINE = Kafka SETTINGS kafka_broker_list = 'rc1b-dt0p7ntrbdum3iqb.mdb.yandexcloud.net:9091',
                              kafka_topic_list = 'films_progress',
                              kafka_group_name = 'clickhouse',
                              kafka_format = 'JSONEachRow';

  CREATE TABLE IF NOT EXISTS shard.films_progress(
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard1/films_progress', 'replica_progress_1')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS replica.films_progress(
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
      ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard2/films_progress', 'replica_progress_2')
      PARTITION BY toYYYYMMDD(timestamp)
      ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS default.films_progress (
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
      ) ENGINE = Distributed('ugc_service_cluster', '', films_progress, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_progress_mv TO shard.films_progress AS
      SELECT *, _timestamp as timestamp, _key as key, _topic as topic, _partition as partition
      FROM default.kafka_films_progress;
  

  CREATE TABLE IF NOT EXISTS default.kafka_films_feedbacks (
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8
    ) ENGINE = Kafka SETTINGS kafka_broker_list = 'rc1b-dt0p7ntrbdum3iqb.mdb.yandexcloud.net:9091',
                              kafka_topic_list = 'films_feedbacks',
                              kafka_group_name = 'clickhouse',
                              kafka_format = 'JSONEachRow';

  CREATE TABLE IF NOT EXISTS shard.films_feedbacks(
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard1/films_feedbacks', 'replica_feedback_1')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS films_feedbacks(
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
      ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard2/films_feedbacks', 'replica_feedback_2')
      PARTITION BY toYYYYMMDD(timestamp)
      ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS default.films_feedbacks (
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8,
      key String,
      timestamp DateTime,
      topic String,
      partition UInt64
      ) ENGINE = Distributed('ugc_service_cluster', '', films_feedbacks, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_feedbacks_mv TO shard.films_feedbacks AS
      SELECT *, _timestamp as timestamp, _key as key, _topic as topic, _partition as partition
      FROM default.kafka_films_feedbacks;


EOSQL
