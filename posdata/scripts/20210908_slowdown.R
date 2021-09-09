bxs_ats <- 63241:63400 %>%
  map(get_blocks_and_attestations) %>%
  purrr::transpose() %>%
  map(rbindlist)

bxs <- copy(bxs_ats$block)
bxs[, declared_client := find_client(graffiti)]
bxs %>% fwrite(here::here("data/bxs_slowdown.csv"))
ats <- bxs_ats$attestations
ats %>% fwrite(here::here("data/ats_slowdown.csv"))
block_root_at_slot <- get_block_root_at_slot(bxs)

agg_info <- get_aggregate_info(ats[slot >= 63201 * 32 & slot < 63210 * 32]) %>%
  inner_join(bxs[, .(slot, declared_client)], by = c("slot" = "slot"))

myopic_redundant <- get_myopic_redundant_ats_detail(ats[slot < 63210 * 32]) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot"))

redundant_ats <- get_redundant_ats(ats[slot >= 63201 * 32 & slot < 63210 * 32]) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot"))

strong_redundant_ats <- get_strong_redundant_ats()

ats %>% group_by(slot) %>% summarise(n = n()) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot")) %>%
  group_by(declared_client) %>%
  summarise(mean_aggs = mean(n))