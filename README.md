# SECTION 2
## ER diagram
---
![ER diagram](Section-2/ER-diagram.png)
The following assumptions are made when coming up with this design:

* `total_price` and `total_weight` are not calculated using data stored in the tables `orders` and `items`, but are readily available when a transaction is made
* `item_name` is unique and can be used as primary key to distinguish the different items

## Executing the codes
---
This section requires the Postgres Docker Official Image which can be installed by running ```docker pull postgres``` in the terminal.

Build and run the Dockerfile in this root directory (i.e. parent directory of `Section-2`) using the following commands.
```
docker build -t postgres-db -f Section-2/Dockerfile .

docker run --name postgres-db-container -p 5432:5432 -d postgres-db
```

To run the queries,
```{bash}
cd Section-2/queries

cat query_1.sql | docker exec -i postgres-db-container psql -U postgres -d database

cat query_2.sql | docker exec -i postgres-db-container psql -U postgres -d database
```