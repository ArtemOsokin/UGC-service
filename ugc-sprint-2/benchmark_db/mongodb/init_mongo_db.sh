docker exec -it mongocfg1 bash -c 'echo "rs.initiate\({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]}\)" | mongo'

docker exec -it mongors1n1 bash -c 'echo "rs.initiate\({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]}\)" | mongo'

docker exec -it mongos1 bash -c 'echo "sh.addShard\(\"mongors1/mongors1n1\"\)" | mongo'

docker exec -it mongors2n1 bash -c 'echo "rs.initiate\({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]}\)" | mongo'

docker exec -it mongos1 bash -c 'echo "sh.addShard\(\"mongors2/mongors2n1\"\)" | mongo'

docker exec -it mongors1n1 bash -c 'echo "use ugc-movies" | mongo'

docker exec -it mongos1 bash -c 'echo "sh.enableSharding\(\"ugc-movies\"\)" | mongo'

docker exec -it mongos1 bash -c 'echo "db.createCollection\(\"ugc-movies.bookmarks\"\)" | mongo'
docker exec -it mongos1 bash -c 'echo "sh.shardCollection\(\"ugc-movies.bookmarks\", {\"user_id\": \"hashed\"}\)" | mongo'
docker exec -it mongos1 bash -c 'echo "db.bookmarks.createIndex\({\"bookmarks.film_id\": 1}\)" | mongo'

docker exec -it mongos1 bash -c 'echo "db.createCollection\(\"ugc-movies.reviews\"\)" | mongo'
docker exec -it mongos1 bash -c 'echo "sh.shardCollection\(\"ugc-movies.reviews\", {\"film_id\": \"hashed\"}\)" | mongo'
docker exec -it mongos1 bash -c 'echo "db.reviews.createIndex\({\"film_id\": 1, \"author\": 1}\)" | mongo'

docker exec -it mongos1 bash -c 'echo "db.createCollection\(\"ugc-movies.film_likes\"\)" | mongo'
docker exec -it mongos1 bash -c 'echo "sh.shardCollection\(\"ugc-movies.film_likes\", {\"film_id\": \"hashed\"}\)" | mongo'
docker exec -it mongos1 bash -c 'echo "db.reviews.createIndex\({\"user_id\": 1}\)" | mongo'

docker exec -it mongos1 bash -c 'echo "db.createCollection\(\"ugc-movies.review_likes\"\)" | mongo'
docker exec -it mongos1 bash -c 'echo "sh.shardCollection\(\"ugc-movies.review_likes\", {\"review_id\": \"hashed\"}\)" | mongo'