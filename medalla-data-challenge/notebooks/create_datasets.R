library(tidyverse)
library(here)
library(RPostgres)
library(DBI)
library(data.table)

source(here::here("notebooks/lib.R"))
source(here::here("notebooks/pw.R"))

con <- dbConnect(RPostgres::Postgres(), user="chain", password=pw)

until_epoch <- 12125
slot_chunk_res <- 1000
epoch_resolution <- 100
slots_per_epoch <- 32
until_slot <- until_epoch * slots_per_epoch
slots_per_year <- 365.25 * 24 * 60 * 60 / 12
epochs_per_year <- slots_per_year / slots_per_epoch
start_suffix <- 1
end_suffix <- 281
datadir <- "data"

### all_bxs

all_bxs <- (start_suffix:end_suffix) %>%
  map(function(i) fread(here::here(str_c(datadir, "/blocks_", i, ".csv"))) %>%
        filter(slot <= until_slot) %>%
        mutate(
          block_root = str_trunc(block_root, 10, "left", ellipsis = ""),
          parent_root = str_trunc(parent_root, 10, "left", ellipsis = ""),
          state_root = str_trunc(state_root, 10, "left", ellipsis = "") 
        )) %>%
  bind_rows()
all_bxs %>% fwrite(here::here("rds_data/all_bxs.csv"))

### all_ats

all_ats <- (start_suffix:end_suffix) %>%
  map(function(i) fread(here::here(str_c(datadir, "/attestations_", i, ".csv"))) %>%
        .[slot <= until_slot,] %>%
        mutate(beacon_block_root = str_trunc(beacon_block_root, 10, "left", ellipsis = ""),
               source_block_root = str_trunc(source_block_root, 10, "left", ellipsis = ""),
               target_block_root = str_trunc(target_block_root, 10, "left", ellipsis = ""),
               contained_ats = str_count(attesting_indices, "1"))) %>%
  bind_rows()
all_ats %>% fwrite(here::here("rds_data/all_ats.csv"))

### all_vs

capture_validators <- function(df) {
  df %>%
    rowwise() %>%
    mutate(pubkey = str_c(c("0x", raw2hex(f_public_key)), collapse="")) %>%
    ungroup() %>%
    select(pubkey, validator_index = f_index, activation_epoch = f_activation_epoch,
           exit_epoch = f_exit_epoch) %>%
    mutate(exit_epoch = as.numeric(exit_epoch),
           last_epoch = if_else(exit_epoch == -1, until_epoch, pmin(exit_epoch, until_epoch)),
           validator_index = as.numeric(validator_index),
           activation_epoch = as.numeric(activation_epoch),
           time_active = last_epoch - activation_epoch)
}

res <- dbSendQuery(con, "SELECT * FROM t_validators")
all_vs <- dbFetch(res, n = 1000) %>% capture_validators()
while(!dbHasCompleted(res)){
  all_vs <- all_vs %>%
    bind_rows(dbFetch(res, n = 1000) %>% capture_validators())
}
all_vs %>% fwrite(here::here("rds_data/all_vs.csv"))

### all_dps

all_dps <- (start_suffix:end_suffix) %>%
  map(function(i) fread(here::here(str_c(datadir, "/deposits_", i, ".csv"))) %>%
        filter(slot <= until_slot) %>%
        left_join(
          all_vs,
          by = c("pubkey" = "pubkey")
        ) %>%
        select(validator_index, deposit_slot = slot, amount)
  ) %>%
  bind_rows() %>%
  ungroup()
all_dps %>% fwrite(here::here("rds_data/all_dps.csv"))

### block_root_at_slot

tibble(
  slot = 0:until_slot
) %>%
  left_join(
    all_bxs %>% select(slot, block_root),
    by = c("slot" = "slot")
  ) %>%
  mutate(block_root = .$block_root %>% na.locf()) %>%
  write_csv(here::here("rds_data/block_root_at_slot.csv"))

### logical_ats

logical_ats <- batch_ops(
  all_ats,
  function(df) df$attesting_indices %>%
    str_extract_all("[01]") %>%
    map(strtoi) %>%
    map(as.logical) %>%
    plyr::ldply(rbind) %>%
    add_column(
      slot = df$slot,
      att_slot = df$att_slot,
      committee_index = df$committee_index,
      beacon_block_root = df$beacon_block_root,
      source_block_root = df$source_block_root,
      target_block_root = df$target_block_root, .before = "1")
) %>%
  arrange(att_slot, committee_index, slot)
logical_ats %>% fwrite(here::here("rds_data/logical_ats.csv"))

### exploded_ats

batch_size <- 1e3
batches <- until_slot %/% batch_size
for (batch in 0:batches) {
  print(str_c(batch, " batch out of ", batches, " batches"))
  logical_ats %>%
    filter(
      att_slot >= batch * batch_size, att_slot < (batch + 1) * batch_size
    ) %>%
    pivot_longer(matches("[0-9]+"), names_to = "index_in_committee") %>%
    drop_na() %>%
    filter(value) %>%
    select(-value) %>%
    mutate(index_in_committee = strtoi(index_in_committee) - 1) %>%
    fwrite(here::here(str_c("rds_data/exploded_ats_", batch, ".csv")))
}

### individual_ats

for (batch in 0:387) {
  print(str_c(batch, " batch out of 387 batches"))
  
  t <- fread(str_c("rds_data/exploded_ats_", batch, ".csv"))
  
  comm <- dbGetQuery(
    con,
    str_c(
      "SELECT * FROM t_beacon_committees WHERE f_slot >= ",
      t %>% summarise(min(att_slot)) %>% pull(1) %>% pluck(1),
      " AND f_slot <= ",
      t %>% summarise(max(att_slot)) %>% pull(1) %>% pluck(1)
    )
  ) %>% capture_committee() %>%
    select(-epoch) %>%
    as.data.table()
  
  t %>%
    .[, .(min_inclusion_slot=min(slot)),
      by=.(att_slot, committee_index, index_in_committee,
           beacon_block_root, source_block_root, target_block_root)] %>%
    .[, epoch:=att_slot %/% slots_per_epoch] %>%
    .[, epoch_slot:=epoch * slots_per_epoch] %>%
    merge(comm) %>%
    merge(
      fread(here::here("rds_data/block_root_at_slot.csv")) %>%
        .[, correct_target:=1],
      by.x = c("epoch_slot", "target_block_root"),
      by.y = c("slot", "block_root"),
      all.x = TRUE
    ) %>%
    .[, `:=`(epoch = NULL, epoch_slot = NULL)] %>%
    merge(
      fread(here::here("rds_data/block_root_at_slot.csv")) %>%
        .[, correct_head:=1],
      by.x = c("att_slot", "beacon_block_root"),
      by.y = c("slot", "block_root"),
      all.x = TRUE
    ) %>%
    setnafill("const", 0, cols=c("correct_target", "correct_head")) %>%
    fwrite(here::here(str_c("rds_data/individual_ats_", batch, ".csv")))
}

### expected_ats

expected_ats <- batch_ops(
  tibble(
    slot = 0:until_slot
  ), function(df) {
    dbGetQuery(
      con,
      str_c(
        "SELECT * FROM t_beacon_committees WHERE f_slot >= ",
        df %>% summarise(min(slot)) %>% pull(1) %>% pluck(1),
        " AND f_slot <= ",
        df %>% summarise(max(slot)) %>% pull(1) %>% pluck(1)
      )
    ) %>%
      capture_committee() %>%
      group_by(att_slot, committee_index) %>%
      summarise(expected_ats = n())
  },
  batch_size = 1000
)
expected_ats %>% fwrite(here::here("rds_data/expected_ats.csv"))

# How many individual attestations are there?

batch_ops_ats(
  function(df) df %>%
    .[, .(count=.N)]
) %>%
  .[, .(count=sum(count))] %>%
  pull(count) %>%
  pluck(1) %>%
  saveRDS(here::here("rds_data/n_individual_ats.rds"))

# In how many aggregates does an individual attestation appear?

batch_ops_ats(function(df) {
  df %>%
    .[, .(appearances=.N),
      by=.(att_slot, committee_index, index_in_committee,
           beacon_block_root, source_block_root, target_block_root)] %>%
    .[, .(count=.N), by=appearances]
}, dataset = "exploded") %>%
  .[, .(count=sum(count)), by=.(appearances)] %>%
  fwrite(here::here("rds_data/appearances_in_aggs.csv"))

# How many redundant aggregate attestations are there?

all_ats %>%
  .[, .(appearances=.N),
    by=.(att_slot, committee_index,
         beacon_block_root, source_block_root, target_block_root, attesting_indices)] %>%
  .[, .(count=.N), by=.(appearances)] %>%
  fwrite(here::here("rds_data/redundant_ats.csv"))

# How many times did a block include the exact same aggregate attestation more than once?

all_ats %>%
  .[, .(appearances=.N),
    by=.(slot, att_slot, committee_index,
         beacon_block_root, source_block_root, target_block_root, attesting_indices)] %>%
  .[, .(count=.N), by=.(appearances)] %>%
  fwrite(here::here("rds_data/appearances_in_same_block.csv"))

# How many times were clashing attestations included in blocks?

all_ats %>%
  unique() %>%
  .[, .(appearances=.N),
    by=.(slot, att_slot, committee_index,
         beacon_block_root, source_block_root, target_block_root)] %>%
  .[, .(count=.N), by=.(appearances)] %>%
  fwrite(here::here("rds_data/weakly_clashing.csv"))

# Inclusion delay histogram

batch_ops_ats(function(df) {
  df %>%
    .[, .(inclusion_delay=min_inclusion_slot-att_slot)] %>%
    .[, .(count=.N), by=inclusion_delay]
}) %>%
  .[, .(count=sum(count)), by=inclusion_delay] %>%
  fwrite(here::here("rds_data/inclusion_delay_hist.csv"))

# stats_per_val

batch_ops_ats(function(df) {
  df %>%
    .[, inclusion_delay:=(min_inclusion_slot-att_slot)] %>%
    .[, .(
      count=.N, delay=sum(inclusion_delay),
      first_att=min(att_slot), last_att=max(att_slot),
      correct_targets=sum(correct_target), correct_heads=sum(correct_head)
    ), by=.(validator_index)]
}) %>%
  .[, .(
    avg_delay=(sum(delay) / sum(count)),
    included_ats=sum(count),
    first_att=min(first_att), last_att=max(last_att),
    correct_targets=sum(correct_targets), correct_heads=sum(correct_heads)
  ), by=.(validator_index)] %>%
  fwrite(here::here("rds_data/stats_per_val.csv"))

# stats_per_slot

batch_ops_ats(function(df) {
  df %>%
    .[, .(
      included_ats=.N,
      correct_targets=sum(correct_target),
      correct_heads=sum(correct_head)
    ), by=att_slot]
}) %>%
  merge(expected_ats %>%
          group_by(att_slot) %>%
          summarise(expected_ats = sum(expected_ats)),
        all.y = TRUE) %>%
  setnafill(type = "const", fill = 0, cols=c("included_ats", "correct_targets", "correct_heads")) %>%
  fwrite(here::here("rds_data/stats_per_slot.csv"))
  
  
  
  
  
  