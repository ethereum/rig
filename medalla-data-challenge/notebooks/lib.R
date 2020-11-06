library(BMS)
library(tidyverse)
library(data.table)
library(httr)
library(jsonlite)
library(vroom)
library(zoo)
library(lubridate)
library(microbenchmark)

slots_per_epoch <- 32
medalla_genesis <- 1596546008

get_date_from_epoch <- function(epoch) {
  return(as_datetime(epoch * slots_per_epoch * 12 + medalla_genesis))
}

get_epoch_from_timestamp <- function(timestamp) {
  return((timestamp - medalla_genesis) / (slots_per_epoch * 12))
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
  warning(str_c("Getting committee of epoch ", epoch, "\n"))
  content(GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
            epoch * slots_per_epoch, "/committees/", epoch)))$data %>%
    rbindlist() %>%
    select(att_slot = slot, committee_index = index, validator_index = validators) %>%
    mutate_all(as.numeric) %>%
    group_by(att_slot, committee_index) %>%
    mutate(index_in_committee = row_number() - 1)
}

get_validators <- function(epoch) {
  t <- (content(GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
                    epoch * slots_per_epoch, "/validators")), as="text") %>%
    fromJSON())$data
  cbind(t[c("index", "balance")], t$validator) %>%
    select(validator_index = index, balance, effective_balance, slashed, activation_epoch, exit_epoch) %>%
    mutate_all(as.numeric) %>%
    mutate(time_active = pmin(exit_epoch, epoch) - pmin(epoch, activation_epoch)) %>%
    as.data.table()
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

get_exploded_ats <- function(all_ats) {
  exploded_ats <- copy(all_ats[att_slot <= 0,])
  
  exploded_ats[, agg_index:=.I]
  exploded_ats <- exploded_ats[
    , .(attested=as.numeric(unlist(strsplit(attesting_indices, "")))),
    by=setdiff(names(exploded_ats), "attesting_indices")
  ]
  exploded_ats[, index_in_committee:= rowid(agg_index) - 1]
  
  return(exploded_ats[attested==1,])
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
  warning(str_c("Blocks and attestations of epoch ", epoch, "\n"), immediate. = TRUE)
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  t <- start_slot:end_slot %>%
    map(get_block_and_attestations_at_slot) %>%
    keep(is.list) %>%
    purrr::transpose()
  list(
    blocks = rbindlist(t$block),
    attestations = rbindlist(t$attestations)
  )
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

get_correctness_data <- function(all_ats, block_root_at_slot) {
  all_ats %>%
    .[, epoch:=att_slot %/% slots_per_epoch] %>%
    .[, epoch_slot:=epoch * slots_per_epoch] %>%
    merge(
      block_root_at_slot %>%
        .[, .(slot, block_root, correct_target=1)],
      by.x = c("epoch_slot", "target_block_root"),
      by.y = c("slot", "block_root"),
      all.x = TRUE
    ) %>%
    .[, `:=`(epoch = NULL, epoch_slot = NULL)] %>%
    merge(
      block_root_at_slot %>%
        .[, .(slot, block_root, correct_head=1)],
      by.x = c("att_slot", "beacon_block_root"),
      by.y = c("slot", "block_root"),
      all.x = TRUE
    ) %>%
    setnafill("const", 0, cols=c("correct_target", "correct_head"))
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

# t <- batch_ops_per_slot(
#   all_ats,
#   function(df) {
#     if (nrow(df) == 0) {
#       return(NULL)
#     }
#     df %>%
# group_by(slot, att_slot, committee_index,
# beacon_block_root, source_block_root, target_block_root) %>%
#       nest() %>%
#       mutate(includes = map(data, compare_ats),
#              n_subset = map(includes, count_subset) %>% unlist(),
#              n_subset_ind = map(includes, count_subset_ind) %>% unlist(),
#              n_strongly_clashing = map(includes, count_strongly_clashing) %>% unlist(),
#              n_weakly_clashing = map(includes, count_weakly_clashing) %>% unlist()) %>%
#       filter(n_subset > 0 | n_strongly_clashing > 0 | n_weakly_clashing > 0) %>%
#       select(slot, att_slot, committee_index, beacon_block_root,
#              source_block_root, target_block_root,
#              n_subset, n_subset_ind, n_strongly_clashing, n_weakly_clashing) %>%
#       return()
#   },
#   from_slot = 590000,
#   to_slot = 610000
# ) %>%
#   select(slot, att_slot, committee_index, beacon_block_root,
#          source_block_root, target_block_root,
#          n_subset, n_subset_ind, n_strongly_clashing, n_weakly_clashing) %>%
#   union(fread(here::here("rds_data/subset_ats.csv"))) %>%
#   fwrite(here::here("rds_data/subset_ats.csv"))
# 
# fread(here::here("rds_data/subset_ats_30000.csv")) %>%
#   union(fread(here::here("rds_data/subset_ats_590000+.csv"))) %>%
#   fwrite(here::here("rds_data/subset_ats.csv"))
# 
# # Try that it is correct with a small example
# t <- tibble(indices = list(c(T,T), c(T,F)))