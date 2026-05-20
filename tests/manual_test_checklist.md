# Manual Test Checklist

## Part 1 — catalog

- [ ] Search valid topic returns `200` with `id` and `title` only
- [ ] Search invalid topic returns `404`
- [ ] Info valid item returns full book fields
- [ ] Info invalid item returns `404`
- [ ] Update quantity, price, or both returns `200`
- [ ] Catalog data persists after restart

## Part 1 — order and front-end

- [ ] Purchase in stock returns `201` through front-end
- [ ] Purchase invalid item returns `404`
- [ ] Purchase out of stock returns `409`
- [ ] Catalog quantity decreases after purchase
- [ ] Order log records successful purchases only
- [ ] Front-end is the only client entry point on port `5000`

## Part 1 — Docker

- [ ] `docker compose up catalog_service` works on port `5001`

## Lab 2 — replicas

- [ ] Two catalog replicas run on `5001` and `5011`
- [ ] Two order replicas run on `5002` and `5012`
- [ ] Catalog update on replica 1 appears on replica 2
- [ ] Catalog update on replica 2 appears on replica 1
- [ ] Purchase on order replica 1 appears in both order logs
- [ ] Purchase on order replica 2 appears in both order logs

## Lab 2 — front-end

- [ ] Round-robin alternates catalog replicas on reads
- [ ] Round-robin alternates order replicas on purchases
- [ ] First read is cache `miss`, second is `hit`
- [ ] Purchase invalidates cache; next read is `miss` with new quantity
- [ ] `X-Cache-Status` and `X-Response-Time-Ms` headers present on reads

## Lab 2 — Docker

- [ ] `docker compose -f docker-compose.lab2.yml up` starts full stack
- [ ] Client requests work through `http://127.0.0.1:5000`
