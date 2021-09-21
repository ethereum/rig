source("notebooks/lib.R")

myred <- "#F05431"
myyellow <- "#FED152"
mygreen <- "#BFCE80"
client_colours <- c("#000011", "#ff9a02", "#eb4a9b", "#7dc19e", "grey", "red")

# Get blocks
t2 <- 61001:62000 %>%
  map(get_blocks) %>%
  rbindlist()
list(fread(here::here("data/pyrmont_bxs.csv")), t2) %>%
  rbindlist() %>%
  fwrite(here::here("data/pyrmont_bxs.csv"))
pyrmont_bxs <- fread(here::here("data/pyrmont_bxs.csv"))
pyrmont_bxs[, declared_client := find_client(graffiti)]

t <- seq(65051, 68000, 10) %>%
  map(function(epoch) {
    bxs <- get_blocks(epoch, sync_committee = TRUE)
    bxs[, epoch := epoch]
    exploded_bxs <- get_exploded_sync_block(bxs)
    sync_committee <- get_sync_committee(epoch)
    exploded_bxs %>% inner_join(sync_committee)
  }) %>%
  rbindlist()
list(fread(here::here("data/pyrmont_scs.csv")), t) %>%
  rbindlist() %>%
  fwrite(here::here("data/pyrmont_scs.csv"))
pyrmont_scs <- fread(here::here("data/pyrmont_scs.csv"))
pyrmont_scs[, proposer_declared_client := find_client(graffiti)]

previous_blk_proposer <- pyrmont_scs[, .(slot)] %>%
  unique() %>%
  mutate(previous_slot = slot - 1) %>%
  inner_join(pyrmont_scs[, .(slot, graffiti)] %>% unique() %>% copy(), by = c("previous_slot" = "slot")) %>% copy()
previous_blk_proposer[, previous_proposer_declared_client := find_client(graffiti)]

pyrmont_scs %>%
  group_by(validator_index) %>%
  summarise(percent_correct_sync = sum(sync_committeed) / n()) %>%
  inner_join(pyrmont_bxs %>% select(validator_index = proposer_index,
                                    syncer_declared_client = declared_client)) %>%
  group_by(syncer_declared_client) %>%
  summarise(mean_pc = mean(percent_correct_sync), n_obs = n()) %>%
  ggplot() +
  geom_col(aes(x = syncer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  scale_fill_manual(values = client_colours)
  
pyrmont_scs %>%
  inner_join(previous_blk_proposer %>% select(slot, previous_proposer_declared_client)) %>%
  inner_join(pyrmont_bxs %>% select(validator_index = proposer_index,
                                    syncer_declared_client = declared_client)) %>%
  group_by(previous_proposer_declared_client, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_col(aes(x = previous_proposer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  facet_wrap(vars(syncer_declared_client)) +
  scale_fill_manual(values = client_colours)

pyrmont_scs %>%
  inner_join(pyrmont_bxs %>% select(validator_index = proposer_index,
                                    syncer_declared_client = declared_client)) %>%
  group_by(proposer_declared_client, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_col(aes(x = proposer_declared_client, y = mean_pc, fill = syncer_declared_client)) +
  facet_wrap(vars(syncer_declared_client)) +
  scale_fill_manual(values = client_colours)

pyrmont_scs %>%
  inner_join(pyrmont_bxs %>% select(validator_index = proposer_index,
                                    syncer_declared_client = declared_client)) %>%
  group_by(epoch, syncer_declared_client) %>%
  summarise(mean_pc = sum(sync_committeed) / n()) %>%
  ggplot() +
  geom_line(aes(x = epoch, y = mean_pc, color = syncer_declared_client)) +
  scale_color_manual(values = client_colours)