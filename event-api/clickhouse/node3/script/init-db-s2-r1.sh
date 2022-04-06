#!/bin/bash
set -e

clickhouse client -n <<-EOSQL

  CREATE DATABASE IF NOT EXISTS db_shard2;

  CREATE TABLE IF NOT EXISTS default.kafka_films_bookmarks (
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8
    ) ENGINE = Kafka SETTINGS kafka_broker_list = 'rc1b-dt0p7ntrbdum3iqb.mdb.yandexcloud.net:9091',
                              kafka_topic_list = 'films_bookmarks',
                              kafka_group_name = 'clickhouse',
                              kafka_format = 'JSONEachRow';

  CREATE TABLE IF NOT EXISTS db_shard2.films_bookmarks(
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8,
      key String,
      timestamp DateTime
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_bookmarks', '{replica}')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;

  CREATE TABLE IF NOT EXISTS default.films_bookmarks (
      user_id UUID,
      film_id UUID,
      add_to_bookmark UInt8,
      key String,
      timestamp DateTime
    ) ENGINE = Distributed('ugc_service_cluster', '', films_bookmarks, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_bookmarks_mv TO db_shard2.films_bookmarks AS
      SELECT *, _timestamp as timestamp, _key as key
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

  CREATE TABLE IF NOT EXISTS db_shard2.films_progress(
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8,
      key String,
      timestamp DateTime
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_progress', '{replica}')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;


  CREATE TABLE IF NOT EXISTS default.films_progress (
      user_id UUID,
      film_id UUID,
      viewing_progress Int32,
      viewing_language String,
      watched UInt8,
      key String,
      timestamp DateTime
      ) ENGINE = Distributed('ugc_service_cluster', '', films_progress, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_progress_mv TO db_shard2.films_progress AS
      SELECT *, _timestamp as timestamp, _key as key
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

  CREATE TABLE IF NOT EXISTS db_shard2.films_feedbacks(
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8,
      key String,
      timestamp DateTime
    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/films_feedbacks', '{replica}')
    PARTITION BY toYYYYMMDD(timestamp)
    ORDER BY user_id;


  CREATE TABLE IF NOT EXISTS default.films_feedbacks (
      user_id UUID,
      film_id UUID,
      user_rating Float32,
      feedback String,
      like_it UInt8,
      key String,
      timestamp DateTime
      ) ENGINE = Distributed('ugc_service_cluster', '', films_feedbacks, rand());

  CREATE MATERIALIZED VIEW IF NOT EXISTS default.films_feedbacks_mv TO db_shard2.films_feedbacks AS
      SELECT *, _timestamp as timestamp, _key as key
      FROM default.kafka_films_feedbacks;


EOSQL