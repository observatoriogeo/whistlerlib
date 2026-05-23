# 06 — Mention co-occurrence network

The mirror of example 05 but for `@user` mentions. Same coonet algorithm, same igraph result type. Useful as a clean side-by-side comparison: hashtag networks describe **topics**, mention networks describe **conversation partners**.

## What you'll see

```
Loaded 10 tweets.
Graph: 10 nodes, 10 edges.

Edges (source, target, weight):
   source   target  weight
   @gob   @hacienda      1
   @gob     @senado      2
   ...
```

## Run it

```bash
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
uv run pytest -m docker .
```
