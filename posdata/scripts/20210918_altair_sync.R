source("notebooks/lib.R")

myred <- "#F05431"
myyellow <- "#FED152"
mygreen <- "#BFCE80"
client_colours <- c("#000011", "yellow", "#ff9a02", "#eb4a9b", "#7dc19e", "grey", "red")

testnet <- "prater"

# Get blocks
t_testnet_bxs <- 61001:62000 %>%
  map(get_blocks) %>%
  rbindlist()
list(fread(here::here(str_c("data/", testnet , "_bxs.csv"))), t_testnet_bxs) %>%
  rbindlist() %>%
  fwrite(here::here(str_c("data/", testnet , "_bxs.csv")))
testnet_bxs <- fread(here::here(str_c("data/", testnet , "_bxs.csv")))
testnet_bxs[, declared_client := find_client(graffiti)]

testnet_clients <- if (testnet == "pyrmont") testnet_bxs %>%
  select(validator_index = proposer_index, declared_client) %>%
  filter(validator_index > (if(testnet == "pyrmont") 19899 else 200999)) %>%
  union(fread(here::here(str_c("data/", testnet , "_client_map.csv")))) %>%
  unique() %>%
  group_by(validator_index) %>%
  filter(n() == 1) %>%
  ungroup() else fread(here::here(str_c("data/", testnet , "_client_map.csv")))

t_scs <- seq(40700, 40970, 10) %>%
  map(function(epoch) {
    bxs <- get_blocks(epoch, sync_committee = TRUE)
    bxs[, epoch := epoch]
    exploded_bxs <- get_exploded_sync_block(bxs)
    sync_committee <- get_sync_committee(epoch)
    exploded_bxs %>% inner_join(sync_committee)
  }) %>%
  rbindlist()
list(fread(here::here(str_c("data/", testnet , "_scs.csv"))), t_scs) %>%
  rbindlist() %>%
  fwrite(here::here(str_c("data/", testnet , "_scs.csv")))
scs <- fread(here::here(str_c("data/", testnet , "_scs.csv")))
scs[, proposer_declared_client := find_client(graffiti)]

previous_blk_proposer <- scs[, .(slot)] %>%
  unique() %>%
  mutate(previous_slot = slot - 1) %>%
  inner_join(scs[, .(slot, graffiti)] %>% unique() %>% copy(), by = c("previous_slot" = "slot")) %>% copy()
previous_blk_proposer[, previous_proposer_declared_client := find_client(graffiti)]

t_scs %>%
  group_by(validator_index) %>%
  summarise(percent_correct_sync = sum(sync_committeed) / n()) %>%
  inner_join(testnet_clients %>% select(
    validator_index,
    syncer_declared_client = declared_client
  )) %>%
  group_by(syncer_declared_client) %>%
  summarise(mean_pc = mean(percent_correct_sync), n_obs = n()) %>%
  ggplot() +
  geom_col(aes(x = syncer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  scale_fill_manual(values = client_colours)
  
scs %>%
  inner_join(previous_blk_proposer %>% select(slot, previous_proposer_declared_client)) %>%
  inner_join(testnet_clients %>% select(
    validator_index,
    syncer_declared_client = declared_client
  )) %>%
  group_by(previous_proposer_declared_client, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_col(aes(x = previous_proposer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  facet_wrap(vars(syncer_declared_client)) +
  scale_fill_manual(values = client_colours)

scs %>%
  inner_join(testnet_clients %>% select(
    validator_index,
    syncer_declared_client = declared_client
  )) %>%
  group_by(proposer_declared_client, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_col(aes(x = proposer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  facet_wrap(vars(syncer_declared_client)) +
  scale_fill_manual(values = client_colours)

t_scs %>%
  inner_join(testnet_clients %>% select(
    validator_index,
    syncer_declared_client = declared_client
  )) %>%
  group_by(epoch, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_line(aes(x = epoch, y = mean_pc, color = syncer_declared_client)) +
  scale_color_manual(values = client_colours)