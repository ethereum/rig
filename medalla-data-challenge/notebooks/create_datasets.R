library(tidyverse)
library(here)
library(RPostgres)
library(DBI)
library(data.table)

options(dplyr.summarise.inform=F)

source(here::here("notebooks/lib.R"))
source(here::here("notebooks/pw.R"))

con <- dbConnect(RPostgres::Postgres(), user="chain", password=pw)

until_epoch <- 12125
slot_chunk_res <- 1000
epoch_resolution <- 100
slots_per_epoch <- 32
until_slot <- 610000
slots_per_year <- 365.25 * 24 * 60 * 60 / 12
epochs_per_year <- slots_per_year / slots_per_epoch
start_suffix <- 1
end_suffix <- 409
datadir <- "data"

### all_bxs

all_bxs <- (start_suffix:end_suffix) %>%
  map(function(i) fread(here::here(str_c(datadir, "/blocks_", i, ".csv"))) %>%
        mutate(
          block_root = str_trunc(block_root, 10, "left", ellipsis = ""),
          parent_root = str_trunc(parent_root, 10, "left", ellipsis = ""),
          state_root = str_trunc(state_root, 10, "left", ellipsis = ""),
          declared_client = case_when(
            (str_starts(graffiti, "poap") & str_ends(graffiti, "a")) |
              str_detect(graffiti, "prysm") ~ "prysm",
            (str_starts(graffiti, "poap") & str_ends(graffiti, "b")) |
              str_detect(graffiti, "lighthouse") ~ "lighthouse",
            (str_starts(graffiti, "poap") & str_ends(graffiti, "c")) |
              str_detect(graffiti, "teku") ~ "teku",
            (str_starts(graffiti, "poap") & str_ends(graffiti, "d")) |
              str_detect(graffiti, "nimbus") ~ "nimbus",
            (str_starts(graffiti, "poap") & str_ends(graffiti, "e")) |
              str_detect(graffiti, "lodestar") ~ "lodestar",
            TRUE ~ "undecided"
          )
        )) %>%
  bind_rows()
all_bxs %>% fwrite(here::here("rds_data/all_bxs.csv"))

### all_ats

all_ats <- (start_suffix:end_suffix) %>%
  map(function(i) fread(here::here(str_c(datadir, "/attestations_", i, ".csv"))) %>%
        mutate(beacon_block_root = str_trunc(beacon_block_root, 10, "left", ellipsis = ""),
               source_block_root = str_trunc(source_block_root, 10, "left", ellipsis = ""),
               target_block_root = str_trunc(target_block_root, 10, "left", ellipsis = ""),
               contained_ats = str_count(attesting_indices, "1"))
      ) %>%
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
  slot = 0:max(all_bxs$slot)
) %>%
  left_join(
    all_bxs %>% select(slot, block_root),
    by = c("slot" = "slot")
  ) %>%
  mutate(block_root = .$block_root %>% na.locf()) %>%
  fwrite(here::here("rds_data/block_root_at_slot.csv"))

### Includes

compare_ats <- function(bunch) {
  if (nrow(bunch) == 1) {
    return(NULL)
  }
  
  t <- bunch %>%
    pull(attesting_indices) %>%
    str_extract_all("[01]") %>%
    map(strtoi) %>%
    map(as.logical) %>%
    tibble(indices = .)

  t %>%
    mutate(group = 1,
           agg_index = row_number()) %>%
    full_join(t %>%
                mutate(group = 1,
                       agg_index = row_number()),
              by = c("group" = "group")) %>%
    filter(agg_index.x < agg_index.y) %>%
    rowwise() %>%
    mutate(or_op = list(indices.x | indices.y),
           are_same = identical(indices.x, indices.y),
           x_in_y = identical(indices.y, or_op) & !are_same,
           y_in_x = identical(indices.x, or_op) & !are_same,
           and_op = list(indices.x & indices.y),
           intersection_empty = (sum(and_op) == 0),
           subset_is_individual = case_when(
             x_in_y & sum(indices.x) == 1 ~ TRUE,
             y_in_x & sum(indices.y) == 1 ~ TRUE,
             TRUE ~ FALSE
           ),
           strongly_clashing = (!intersection_empty & !x_in_y & !y_in_x),
           weakly_clashing = (intersection_empty & !x_in_y & !y_in_x)) %>%
    select(agg_index.x, agg_index.y, intersection_empty, are_same, subset_is_individual,
           x_in_y, y_in_x, strongly_clashing, weakly_clashing)
}

count_subset <- function(si) {
  if (is.null(si)) {
    return(0)
  }
  
  si %>%
    pull(x_in_y) %>%
    sum() +
    si %>%
    pull(y_in_x) %>%
    sum() %>%
    return()
}

count_subset_ind <- function(si) {
  if (is.null(si)) {
    return(0)
  }
  
  si %>%
    pull(subset_is_individual) %>%
    sum() %>%
    return()
}

count_strongly_clashing <- function(si) {
  if (is.null(si)) {
    return(0)
  }
  
  si %>%
    filter(strongly_clashing) %>%
    select(agg_index = agg_index.x) %>%
    union(
      si %>%
        filter(strongly_clashing) %>%
        select(agg_index = agg_index.y)
    ) %>%
    distinct() %>%
    nrow() %>%
    return()
}

count_weakly_clashing <- function(si) {
  if (is.null(si)) {
    return(0)
  }
  
  subset_ags <- si %>%
    filter(x_in_y) %>%
    select(agg_index = agg_index.x) %>%
    union(
      si %>%
        filter(y_in_x) %>%
        select(agg_index = agg_index.y)
    ) %>%
    distinct() %>%
    pull(agg_index)
  
  strongly_clashing_ags <- si %>%
    filter(strongly_clashing) %>%
    select(agg_index = agg_index.x) %>%
    union(
      si %>%
        filter(strongly_clashing) %>%
        select(agg_index = agg_index.y)
    ) %>%
    distinct() %>%
    pull(agg_index)
  
  si %>%
    mutate(agg_index = agg_index.x) %>%
    select(agg_index, weakly_clashing) %>%
    union(si %>%
            mutate(agg_index = agg_index.y) %>%
            select(agg_index, weakly_clashing)) %>%
    filter(!(agg_index %in% subset_ags), !(agg_index %in% strongly_clashing_ags)) %>%
    distinct() %>%
    pull(weakly_clashing) %>%
    sum() %>%
    return()
}

# Two attestations, I and J
# Strongly redundant: I = J => Should drop one of the two
# If not: Subset: I \subset J or J \subset I => Should drop the smaller one
# If not: Strongly clashing: I \cap J \neq \emptyset => Cannot aggregate
# If not: Weakly clashing => Can aggregate

t <- batch_ops_per_slot(
  all_ats,
  function(df) {
    if (nrow(df) == 0) {
      return(NULL)
    }
    df %>%
      group_by(slot, att_slot, committee_index, beacon_block_root, source_block_root, target_block_root) %>%
      nest() %>%
      mutate(includes = map(data, compare_ats),
             n_subset = map(includes, count_subset) %>% unlist(),
             n_subset_ind = map(includes, count_subset_ind) %>% unlist(),
             n_strongly_clashing = map(includes, count_strongly_clashing) %>% unlist(),
             n_weakly_clashing = map(includes, count_weakly_clashing) %>% unlist()) %>%
      filter(n_subset > 0 | n_strongly_clashing > 0 | n_weakly_clashing > 0) %>%
      select(slot, att_slot, committee_index, beacon_block_root,
             source_block_root, target_block_root,
             n_subset, n_subset_ind, n_strongly_clashing, n_weakly_clashing) %>%
      return()
  },
  # from_slot = 50000,
  # to_slot = 70000
  from_slot = 590000,
  to_slot = 610000
)

t %>%
  select(slot, att_slot, committee_index, beacon_block_root,
         source_block_root, target_block_root, how_many, how_many_ind) %>%
  union(fread(here::here("rds_data/subset_ats.csv"))) %>%
  fwrite(here::here("rds_data/subset_ats.csv"))

# Try that it is correct with a small example
t <- tibble(indices = list(c(T,T), c(T,F)))

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
  
### Heads and targets

df <- fread(here::here("rds_data/all_ats.csv")) %>%
  .[, epoch:=att_slot %/% slots_per_epoch] %>%
  .[, epoch_slot:=epoch * slots_per_epoch] %>%
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
  setnafill("const", 0, cols=c("correct_target", "correct_head"))
  
  
  
  