library(BMS)
library(tidyverse)
library(data.table)
library(httr)
library(jsonlite)
library(vroom)
library(zoo)
library(lubridate)
library(microbenchmark)

options(digits=10)
options(scipen = 999)

slots_per_epoch <- 32
medalla_genesis <- 1596546008
pyrmont_genesis <- 1605700800

get_date_from_epoch <- function(epoch, testnet="pyrmont") {
  if (testnet == "pyrmont") {
    genesis <- pyrmont_genesis
  } else {
    genesis <- medalla_genesis
  }
  return(as_datetime(epoch * slots_per_epoch * 12 + genesis))
}

get_epoch_from_timestamp <- function(timestamp, testnet="pyrmont") {
  if (testnet == "pyrmont") {
    genesis <- pyrmont_genesis
  } else {
    genesis <- medalla_genesis
  }
  return((timestamp - genesis) / (slots_per_epoch * 12))
}

write_all_ats <- function() {
  (1:429) %>%
    map(function(b) { fread(here::here(str_c("data/attestations_", b, ".csv"))) }) %>%
    rbindlist() %>%
    fwrite(here::here("rds_data/all_ats.csv"))
}

write_all_bxs <- function() {
  (1:429) %>%
    map(function(b) { fread(here::here(str_c("data/blocks_", b, ".csv"))) }) %>%
    rbindlist() %>%
    fwrite(here::here("rds_data/all_bxs.csv"))
}

add_bxs <- function(all_bxs, start_epoch, end_epoch) {
  list(all_bxs %>%
         .[slot < start_epoch * slots_per_epoch],
       start_epoch:end_epoch %>%
         map(function(epoch) { get_blocks(epoch) }) %>%
         rbindlist()
  ) %>%
    rbindlist()
}

add_ats <- function(all_ats, start_epoch, end_epoch) {
  list(all_ats %>%
         .[slot < start_epoch * slots_per_epoch],
       start_epoch:end_epoch %>%
         map(function(epoch) { get_attestations(epoch) }) %>%
         rbindlist()
  ) %>%
    rbindlist()
}

add_bxs_and_ats <- function(start_epoch, end_epoch) {
  start_epoch:end_epoch %>%
    map(function(epoch) { get_blocks_and_attestations(epoch) }) %>%
    reduce(function(a, b) list(
      blocks = list(a$blocks, b$blocks) %>% rbindlist(),
      attestations = list(a$attestations, b$attestations) %>% rbindlist()
    ))
}

add_committees <- function(start_epoch, end_epoch) {
  start_epoch:end_epoch %>%
    map(function(epoch) { get_committees(epoch) }) %>%
    rbindlist()
}

batch_ops <- function(df, fn, filter_fn = NULL, batch_size = 1e4) {
  batches <- nrow(df) %/% batch_size
  (0:batches) %>%
    map(
      function(batch) {
        print(str_c(batch, " batch out of ", batches, " batches"))
        if (is.null(filter_fn)) {
          df %>%
            filter(
              row_number() >= batch * batch_size, row_number() < (batch + 1) * batch_size
            ) %>%
            fn()
        } else {
          df %>%
            filter_fn(batch, batches) %>%
            fn()
        }
      }) %>%
    bind_rows() %>%
    return()
}

batch_ops_per_slot <- function(df, fn, from_slot=0, to_slot=1e6, batch_size = 1e2) {
  batches <- (to_slot - from_slot) / batch_size
  print(str_c(batches, " batches"))
  (0:(batches-1)) %>%
    map(function(batch) {
      print(str_c("Batch ", batch, " out of ", batches, " batches, from slot ",
                  from_slot + batch * batch_size, " to slot ", from_slot + (batch + 1) * batch_size))
      t <- df %>%
        filter(slot >= from_slot + batch * batch_size,
               slot < pmin(from_slot + (batch + 1) * batch_size, to_slot)) %>%
        fn()
      t %>% fwrite(here::here(str_c("rds_data/temp_", batch, ".csv")))
      t %>% return()
    }) %>%
    bind_rows() %>%
    return()
}

batch_ops_ats <- function(fn, dataset = "individual") {
  (0:387) %>%
    map(
      function(batch) {
        print(str_c("batch ", batch, " out of 387"))
        fread(here::here(str_c("rds_data/", dataset, "_ats_", batch, ".csv"))) %>%
          fn()
      }
    ) %>%
    rbindlist()
}

test_ops_ats <- function(fn, dataset = "individual") {
  fread(here::here(str_c("rds_data/", dataset, "_ats_", 0, ".csv"))) %>%
    fn()
}

get_committees <- function(epoch) {
  # print(str_c("Getting committee of epoch ", epoch, "\n"))
  content(GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
            epoch * slots_per_epoch, "/committees")))$data %>%
    rbindlist() %>%
    .[,.(att_slot = as.numeric(slot),
         committee_index = as.numeric(index),
         validator_index = as.numeric(validators),
         index_in_committee = rowid(slot, index) - 1)]
}

get_validators <- function(epoch) {
  t <- (content(GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
                    epoch * slots_per_epoch, "/validators")), as="text") %>%
    fromJSON())$data
  cbind(t[c("index", "balance")], t$validator) %>%
    select(validator_index = index, balance, effective_balance, slashed, activation_epoch, exit_epoch, pubkey) %>%
    mutate(across(-any_of(c("pubkey")), as.numeric)) %>%
    mutate(time_active = pmin(exit_epoch, epoch) - pmin(epoch, activation_epoch)) %>%
    as.data.table()
}

get_balances_active_validators <- function(epoch) {
  get_validators(epoch)[
    time_active > 0 & exit_epoch > epoch,
    .(validator_index, balance, time_active, activation_epoch)
  ]
}

decode_aggregation_bits <- function(ab) {
  gsub('(..)(?!$)', '\\1,', substring(ab, 3), perl=TRUE) %>%
    str_split(",") %>%
    pluck(1) %>%
    lapply(function(d) { rev(hex2bin(d)) }) %>%
    unlist() %>%
    str_c(collapse = "")
}

get_attestations_in_slot <- function(slot) {
  get_block_and_attestations_at_slot()$attestations
}

get_attestations <- function(epoch) {
  print(str_c("Getting attestations for epoch ", epoch))
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  start_slot:end_slot %>%
    map(get_attestations_in_slot) %>%
    rbindlist()
}

get_exploded_ats <- function(t) {
  t[, agg_index := .I]
  t <- t[, .(attested = as.numeric(unlist(strsplit(attesting_indices, "")))), by=setdiff(names(t), "attesting_indices")]
  t[, index_in_committee := rowid(agg_index) - 1]
  return(t[attested == 1, -c("agg_index", "attested")])
}

hex2string <- function(string) {
  intToUtf8(
    strtoi(
      do.call(
        paste0, 
        as.data.frame(
          matrix(
            strsplit(substring(string, 3), split = "")[[1]], 
            ncol=2, 
            byrow=TRUE), 
          stringsAsFactors=FALSE)), 
      base=16L)
  )
}

find_client <- function(graffiti) {
  case_when(
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
}

get_block_at_slot <- function(slot) {
  get_block_and_attestations_at_slot()$block
}

get_block_and_attestations_at_slot <- function(slot) {
  block <- content(GET(str_c("http://localhost:5052/eth/v1/beacon/blocks/", slot)))$data$message
  
  if (as.numeric(block$slot) != slot) {
    return(NULL)
  }
  
  if (length(block$body$attestations) == 0) {
    attestations <- NULL
  } else {
    attestations <- block$body$attestations %>%
      plyr::ldply(data.frame) %>%
      rowwise() %>%
      mutate(attesting_indices = decode_aggregation_bits(aggregation_bits)) %>%
      ungroup() %>%
      mutate(committee_index = as.numeric(data.index),
             att_slot = as.numeric(data.slot), slot = slot,
             beacon_block_root = str_trunc(data.beacon_block_root, 12, "left", ellipsis = ""),
             source_block_root = str_trunc(data.source.root, 12, "left", ellipsis = ""),
             target_block_root = str_trunc(data.target.root, 12, "left", ellipsis = ""),
      ) %>%
      select(slot, att_slot, committee_index,
             beacon_block_root,
             attesting_indices, source_epoch = data.source.epoch,
             source_block_root,
             target_epoch = data.target.epoch,
             target_block_root)
    setDT(attestations)
  }
  
  block_root <- content(GET(str_c("http://localhost:5052/eth/v1/beacon/blocks/", slot, "/root")))$data$root
  
  block <- tibble(
    block_root = str_trunc(block_root, 12, "left", ellipsis = ""),
    parent_root = str_trunc(block$parent_root, 12, "left", ellipsis = ""),
    state_root = str_trunc(block$state_root, 12, "left", ellipsis = ""),
    slot = slot,
    proposer_index = as.numeric(block$proposer_index),
    graffiti = tolower(hex2string(block$body$graffiti)),
  )
  setDT(block)
  
  list(
    block = block,
    attestations = attestations
  )
}

get_blocks_and_attestations <- function(epoch) {
  print(str_c("Blocks and attestations of epoch ", epoch, "\n"))
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  start_slot:end_slot %>%
    map(get_block_and_attestations_at_slot) %>%
    keep(is.list) %>%
    purrr::transpose() %>%
    map(rbindlist)
}

get_blocks <- function(epoch) {
  print(str_c("Getting blocks of epoch ", epoch))
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  start_slot:end_slot %>%
    map(get_block_at_slot) %>%
    rbindlist()
}

get_block_root_at_slot <- function(all_bxs) {
  tibble(
    slot = 0:max(all_bxs$slot)
  ) %>%
    left_join(
      all_bxs %>% select(slot, block_root),
      by = c("slot" = "slot")
    ) %>%
    mutate(block_root = .$block_root %>% na.locf()) %>%
    as.data.table()
}

get_correctness_data <- function(t, block_root_at_slot) {
  t[, epoch := att_slot %/% slots_per_epoch]
  t[, epoch_slot := epoch * slots_per_epoch]
  t[block_root_at_slot, on=c("epoch_slot" = "slot", "target_block_root" = "block_root"), correct_target:=1]
  t[block_root_at_slot, on=c("att_slot" = "slot", "beacon_block_root" = "block_root"), correct_head:=1]
  setnafill(t, "const", 0, cols=c("correct_target", "correct_head"))
  t[, `:=`(epoch = NULL, epoch_slot = NULL)]
}

get_stats_per_val <- function(all_ats, block_root_at_slot, chunk_size = 10) {
  min_epoch <- min(all_ats$att_slot) %/% 32
  max_epoch <- max(all_ats$att_slot) %/% 32
  seq(min_epoch, max_epoch - chunk_size, chunk_size) %>%
    map(function(epoch) {
      # print(str_c("Epoch ", epoch))
      committees <- epoch:(epoch + chunk_size - 1) %>%
        map(get_committees) %>%
        rbindlist()
      validators <- get_validators(epoch + chunk_size - 1)[time_active > 0, .(validator_index, time_active)]
      t <- copy(all_ats[(att_slot >= epoch * slots_per_epoch) & (att_slot < ((epoch + chunk_size) * slots_per_epoch - 1))])
      get_correctness_data(t, block_root_at_slot)
      t <- get_exploded_ats(t)
      t[, .(inclusion_delay=min(slot)-att_slot),
        by=.(att_slot, committee_index, index_in_committee, correct_target, correct_head)] %>%
        .[committees, on=c("att_slot", "committee_index", "index_in_committee"), nomatch = 0] %>%
        .[, .(included_ats=.N,
              correct_targets=sum(correct_target), correct_heads=sum(correct_head),
              inclusion_delay=mean(inclusion_delay)), by=validator_index
        ] %>%
        .[validators, on=c("validator_index"), nomatch = NA] %>%
        setnafill("const", 0, cols=c("included_ats", "correct_targets", "correct_heads")) %>%
        .[, .(validator_index, epoch = epoch + chunk_size, expected_ats=pmin(time_active, chunk_size),
              included_ats, correct_targets, correct_heads, inclusion_delay)]
    }) %>%
    rbindlist()
}

get_stats_per_slot <- function(all_ats, committees, chunk_size = 100) {
  expected_ats <- committees[, .(expected_ats = .N), by=att_slot]
  min_epoch <- min(all_ats$att_slot) %/% 32
  max_epoch <- max(all_ats$att_slot) %/% 32
  seq(min_epoch, max_epoch - chunk_size, chunk_size) %>%
    map(function(epoch) {
      # print(str_c("Epoch ", epoch))
      t <- copy(all_ats[(att_slot >= epoch * slots_per_epoch) & (att_slot < ((epoch + chunk_size) * slots_per_epoch - 1))])
      t <- get_exploded_ats(t)
      t[, .(att_slot, committee_index, index_in_committee, correct_target, correct_head)] %>%
        unique() %>%
        .[, .(included_ats = .N,
              correct_targets = sum(correct_target),
              correct_heads = sum(correct_head)), by=att_slot] %>%
        merge(expected_ats)
    }) %>%
    rbindlist()
}

get_appearances_in_agg <- function(all_ats, chunk_size = 100) {
  min_epoch <- min(all_ats$att_slot) %/% 32
  max_epoch <- max(all_ats$att_slot) %/% 32
  seq(min_epoch, max_epoch - chunk_size, chunk_size) %>%
    map(function(epoch) {
      # print(str_c("Epoch ", epoch))
      t <- copy(all_ats[(att_slot >= epoch * slots_per_epoch) & (att_slot < ((epoch + chunk_size) * slots_per_epoch - 1))])
      t <- get_exploded_ats(t)
      t[, .(appearances=.N),
        by=.(att_slot, committee_index, index_in_committee,
             beacon_block_root, source_block_root, target_block_root)] %>%
        .[, .(count=.N), by=appearances]
    }) %>%
    rbindlist() %>%
    .[, .(count=sum(count)), by=.(appearances)]
}

get_myopic_redundant_ats <- function(all_ats) {
  all_ats %>%
    .[, .(appearances=.N),
      by=.(att_slot, committee_index,
           beacon_block_root, source_block_root, target_block_root, attesting_indices)] %>%
    .[, .(count=.N), by=.(appearances)]
}

get_strong_redundant_ats <- function(all_ats) {
  all_ats %>%
    .[, .(appearances=.N),
      by=.(slot, att_slot, committee_index,
           beacon_block_root, source_block_root, target_block_root, attesting_indices)] %>%
    .[, .(count=.N), by=.(appearances)]
}

### Subset and clashing attestations

# Two attestations, I and J
# Strongly redundant: I = J => Should drop one of the two
# If not: Subset: I \subset J or J \subset I => Should drop the smaller one
# If not: Strongly clashing: I \cap J \neq \emptyset => Cannot aggregate
# If not: Weakly clashing => Can aggregate

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

get_aggregate_info <- function(all_ats) {
  if (nrow(all_ats) == 0) {
    return(NULL)
  }
  
  all_ats %>%
    group_by(slot, att_slot, committee_index,
             beacon_block_root, source_block_root, target_block_root) %>%
    nest() %>%
    mutate(includes = map(data, compare_ats),
           n_subset = map(includes, count_subset) %>% unlist(),
           n_subset_ind = map(includes, count_subset_ind) %>% unlist(),
           n_strongly_clashing = map(includes, count_strongly_clashing) %>% unlist(),
           n_weakly_clashing = map(includes, count_weakly_clashing) %>% unlist()) %>%
    filter(n_subset > 0 | n_strongly_clashing > 0 | n_weakly_clashing > 0) %>%
    select(slot, att_slot, committee_index, beacon_block_root,
           source_block_root, target_block_root,
           n_subset, n_subset_ind, n_strongly_clashing, n_weakly_clashing)
}