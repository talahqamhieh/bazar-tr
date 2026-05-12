# Manual Test Checklist

## Current completed checks

- [ ] Search by valid topic returns `200` with `id` and `title` only
- [ ] Search by invalid topic returns `404` JSON with `message`
- [ ] Info by valid item returns `200` with `id`, `title`, `topic`, `price`, and `quantity`
- [ ] Info by invalid item returns `404` JSON with `message`
- [ ] Update quantity only returns `200` with `message` and updated `item`
- [ ] Update price only returns `200` with `message` and updated `item`
- [ ] Update both price and quantity returns `200`
- [ ] Persistence after restart keeps updated catalog data
- [ ] Docker catalog service starts and answers requests on port `5001`
- [ ] Purchase flow succeeds when stock is available through the front-end
- [ ] Purchase flow returns `409` when stock is unavailable through the front-end
- [ ] Front-end service proxies search and info to catalog
- [ ] Front-end service proxies purchase to order
- [ ] Full three-service local run works end to end through port `5000`

## Upcoming integration checks

- [ ] Full three-service Docker run works end to end
