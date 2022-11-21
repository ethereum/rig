source("notebooks/lib.R")
library(zoo)

myred <- "#F05431"
myyellow <- "#FED152"
mygreen <- "#BFCE80"
client_colours <- c("#000011", "#ff9a02", "#eb4a9b", "#7dc19e", "grey", "red")

bxs_ats <- 63241:63400 %>%
  map(get_blocks_and_attestations) %>%
  purrr::transpose() %>%
  map(rbindlist)

bxs <- copy(bxs_ats$block)
bxs[, declared_client := find_client(graffiti)]
list(fread(here::here("data/bxs_slowdown.csv")), bxs) %>% rbindlist() %>%
  fwrite(here::here("data/bxs_slowdown.csv"))

ats <- bxs_ats$attestations
list(fread(here::here("data/ats_slowdown.csv")), ats) %>% rbindlist() %>%
  fwrite(here::here("data/ats_slowdown.csv"))

bxs <- fread(here::here("data/bxs_slowdown.csv"))
ats <- fread(here::here("data/ats_slowdown.csv"))
block_root_at_slot <- get_block_root_at_slot(bxs)
get_correctness_data(ats, block_root_at_slot)

committees <- 63201:63220 %>%
  map(get_committees) %>%
  rbindlist()

agg_info <- get_aggregate_info(ats[slot < 63250]) %>%
  inner_join(bxs[, .(slot, declared_client)], by = c("slot" = "slot"))

myopic_redundant <- get_myopic_redundant_ats_detail(ats[slot >= 63201 * 32]) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot")) %>%
  mutate(declared_client = if_else(declared_client == "undecided", graffiti, declared_client))

redundant_ats <- get_redundant_ats(ats[slot >= 63201 * 32 & slot < 63221 * 32]) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot")) %>%
  mutate(declared_client = if_else(declared_client == "undecided", graffiti, declared_client))

ats %>% group_by(slot) %>% summarise(n = n()) %>%
  inner_join(bxs[, .(slot, declared_client, graffiti)], by = c("slot" = "slot")) %>%
  group_by(declared_client) %>%
  summarise(mean_aggs = mean(n)) %>%
  ggplot() +
  geom_col(aes(x = declared_client, y = mean_aggs, fill=declared_client)) +
  scale_fill_manual(values = client_colours)

stats_per_slot <- get_stats_per_slot(ats[att_slot >= 63201 * 32 & att_slot < 63220 * 32], committees, chunk_size = 1)

myopic_redundant %>% union(
  bxs %>% mutate(declared_client = if_else(declared_client == "undecided", graffiti, declared_client)) %>%
    anti_join(myopic_redundant %>% select(slot)) %>%
    mutate(n_myopic_redundant = 0) %>%
    select(slot, n_myopic_redundant, declared_client, graffiti)
) %>%
  group_by(declared_client) %>%
  summarise(mean_myopic = mean(n_myopic_redundant),
            n_blocks = n()) %>%
  filter(n_blocks >= 5) %>%
  arrange(-mean_myopic) %>%
  ggplot() +
  geom_col(aes(x = declared_client, y = mean_myopic, fill=declared_client)) +
  guides(fill=FALSE) +
  theme(
    axis.text.x = element_text(
      angle = 90,
      hjust = 1,
      vjust = 0.5
    ))

redundant_ats %>% union(
  bxs %>% mutate(declared_client = if_else(declared_client == "undecided", graffiti, declared_client)) %>%
    anti_join(redundant_ats %>% select(slot)) %>%
    mutate(n_redundant = 0) %>%
    select(slot, n_redundant, declared_client, graffiti)
) %>% group_by(declared_client) %>%
  summarise(mean_redundant = mean(n_redundant),
            n_blocks = n()) %>%
  filter(n_blocks >= 5) %>%
  arrange(-mean_redundant) %>%
  ggplot() +
  geom_col(aes(x = declared_client, y = mean_redundant, fill=declared_client)) +
  guides(fill=FALSE) +
  theme(
    axis.text.x = element_text(
      angle = 90,
      hjust = 1,
      vjust = 0.5
    ))

stats_per_slot %>%
  mutate(slot_in_epoch = att_slot %% 32) %>%
  group_by(slot_in_epoch) %>%
  summarise(correct_target = mean(correct_targets/included_ats)) %>%
  # summarise(correct_head = mean(correct_head)) %>%
  ggplot() +
  geom_col(aes(x = slot_in_epoch, y = correct_target), fill = myred)

stats_per_slot %>%
  mutate(slot_in_epoch = att_slot %% 32) %>%
  filter(slot_in_epoch == 0) %>%
  ggplot() +
  geom_histogram(aes(x = correct_targets/included_ats))

my_sps <- function(epoch) {
  bxs_ats <- (epoch-1):(epoch+1) %>%
    map(get_blocks_and_attestations) %>%
    purrr::transpose() %>%
    map(rbindlist)
  
  bxs <- copy(bxs_ats$block)
  bxs[, declared_client := find_client(graffiti)]
  ats <- copy(bxs_ats$attestations)
  block_root_at_slot <- get_block_root_at_slot(bxs)
  get_correctness_data(ats, block_root_at_slot)
  committees <- epoch:epoch %>%
    map(get_committees) %>%
    rbindlist()
  pre_trans_blk <- bxs %>% filter(slot == epoch * 32 - 1)
  if (pre_trans_blk %>% nrow() == 0) {
    blk_producer = "not produced"
  } else {
    blk_producer = pre_trans_blk$declared_client[1]
  }
  
  trans_blk <- bxs %>% filter(slot == epoch * 32)
  if (trans_blk %>% nrow() == 0) {
    trans_blk_producer = "not produced"
  } else {
    trans_blk_producer = trans_blk$declared_client[1]
  }
  
  stats_per_slot <- get_stats_per_slot(
      ats[att_slot >= epoch * 32], committees, chunk_size = 1
    )[att_slot < (epoch + 1) * 32] %>%
      mutate(pre_trans_blk_producer = blk_producer,
             trans_blk_producer = trans_blk_producer)
  return(stats_per_slot)
}

my_trans_block <- function(epoch) {
  bxs <- get_block_at_slot(epoch * 32)
  if (is.null(bxs)) {
    return(tibble(att_slot = epoch * 32, declared_client = "not produced"))
  } else {
    bxs[, declared_client := find_client(graffiti)] %>%
      mutate(declared_client = if_else(declared_client == "undecided", graffiti, declared_client))
    return(bxs[, .(att_slot = slot, declared_client)])
  }
}

stats_temp <- seq(45050, 64050, 100) %>% map(my_sps) %>% rbindlist()
bxs <- seq(45000, 64000, 100) %>% map(my_trans_block) %>% rbindlist()

stats_per_slot_total <- list(
  stats_per_slot_total,
  stats_temp %>% mutate(epoch = att_slot %/% 32) %>%
    select(att_slot, included_ats, correct_targets, correct_heads,
           expected_ats, pre_trans_blk_producer, epoch, trans_blk_producer)
) %>% rbindlist() %>% arrange(att_slot)



stats_per_slot_total %>%
  mutate(epoch = att_slot %/% 32) %>%
  group_by(epoch, trans_blk_producer) %>%
  summarise(included_ats = sum(included_ats),
            expected_ats = sum(expected_ats),
            correct_targets = sum(correct_targets),
            correct_heads = sum(correct_heads)) %>%
  mutate(percent_voted = included_ats / expected_ats,
         percent_correct_target = correct_targets / included_ats,
         percent_correct_heads = correct_heads / included_ats) %>%
  ggplot() +
  geom_line(aes(x = epoch, y = percent_voted), color = "steelblue")
  # geom_line(aes(x = epoch, y = percent_correct_target), color = "orange") +
  # facet_wrap(vars(trans_blk_producer))

stats_per_slot_total %>%
  filter(att_slot %% 32 == 0) %>%
  group_by(trans_blk_producer) %>%
  summarise(percent_correct = mean(correct_targets / included_ats))

#####

val_ats <- get_exploded_ats(ats[att_slot < 63221 * 32]) %>% left_join(committees, .) %>%
  inner_join(read_csv(here::here("data/stakers.csv"))) %>% select(-slot) %>%
  unique() %>% filter(is.na(correct_head))

val_ats %>% group_by(staker) %>%
  summarise(percent_correct_head = sum(correct_head) / n())

read_csv(here::here("data/stakers.csv")) %>%
  count(staker)