#!/bin/bash
set -e

clickhouse client -n <<-EOSQL

  CREATE DATABASE IF NOT EXISTS db_shard1;

  CREATE TABLE IF NOT EXISTS db_shard1.films_bookmarks(
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



  CREATE TABLE IF NOT EXISTS db_shard1.films_progress(
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


  CREATE TABLE IF NOT EXISTS db_shard1.films_feedbacks(
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


EOSQL
