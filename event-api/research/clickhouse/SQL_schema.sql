CREATE DATABASE test_base;

CREATE DATABASE shard;

CREATE DATABASE replica;

CREATE TABLE shard.test (
    id Int64,
    user_id Int64,
    movies_id Int64,
    movie_mark Int64,
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/test', 'replica_2')
PARTITION BY toYYYYMMDD(event_time)
ORDER BY id;

CREATE TABLE replica.test (
    id Int64,
    user_id Int64,
    movies_id Int64,
    movie_mark Int64,
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/test', 'replica_1')
PARTITION BY toYYYYMMDD(event_time)
ORDER BY id;

CREATE TABLE test_base.test (
    id Int64,
    user_id Int64,
    movies_id Int64,
    movie_mark Int64,
    event_time DateTime
) ENGINE = Distributed('company_cluster', '', test, rand());
