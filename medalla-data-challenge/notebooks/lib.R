library(BMS)

slots_per_epoch <- 32

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

batch_ops_per_slot <- function(df, fn, from_slot=0, to_slot=4e5, batch_size = 1e2) {
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

get_committee <- function(epoch) {
  GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
            epoch * slots_per_epoch, "/committees/", epoch))$content %>%
    rawToChar() %>%
    fromJSON() %>%
    .$data %>%
    as_tibble() %>%
    unnest(validators) %>%
    select(att_slot = slot, committee_index = index, validator_index = validators) %>%
    mutate_all(as.numeric) %>%
    group_by(att_slot, committee_index) %>%
    mutate(index_in_committee = row_number() - 1) %>%
    ungroup() %>%
    filter(committee_index == 11, att_slot == 608e3) %>%
    View()
}

get_validators <- function(epoch) {
  GET(str_c("http://localhost:5052/eth/v1/beacon/states/",
            epoch * slots_per_epoch, "/validators"))$content %>%
    rawToChar() %>%
    fromJSON() %>%
    .$data %>%
    .$validator %>%
    mutate(validator_index = row_number() - 1) %>%
    select(validator_index, effective_balance, slashed, exit_epoch, activation_epoch) %>%
    mutate_all(as.numeric) %>%
    mutate(time_active = pmin(exit_epoch, epoch) - pmax(epoch, activation_epoch))
}

get_attestations_in_slot <- function(slot) {
  # print(str_c("Getting attestations in slot ", slot))
  block_at_slot <- GET(str_c("http://localhost:5052/eth/v1/beacon/blocks/", slot))$content %>%
    rawToChar() %>%
    fromJSON() %>%
    .$data %>%
    .$message %>%
    .$slot %>%
    as.numeric()
  
  if (block_at_slot != slot) {
    return(NULL)
  }
  
  t <- GET(str_c("http://localhost:5052/eth/v1/beacon/blocks/",
            slot, "/attestations"))$content %>%
    rawToChar() %>%
    fromJSON()
  
  if (length(t$data) == 0) {
    return(NULL)
  }
  
  t$data %>%
    jsonlite::flatten() %>%
    rowwise() %>%
    mutate(attesting_indices = substring(str_c(hex2bin(aggregation_bits), collapse=""), 5)) %>%
    ungroup() %>%
    mutate(beacon_block_root = str_trunc(data.beacon_block_root, 12, "left", ellipsis = ""),
           source_block_root = str_trunc(data.source.root, 12, "left", ellipsis = ""),
           target_block_root = str_trunc(data.target.root, 12, "left", ellipsis = ""),
           slot = slot, committee_index = as.numeric(data.index),
           att_slot = as.numeric(data.slot)) %>%
    select(slot, att_slot, committee_index,
           beacon_block_root,
           attesting_indices, source_epoch = data.source.epoch,
           source_block_root,
           target_epoch = data.target.epoch,
           target_block_root)
}

get_attestations <- function(epoch) {
  print(str_c("Getting attestations for epoch ", epoch))
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  start_slot:end_slot %>%
    map(get_attestations_in_slot)
}

get_exploded_ats <- function(all_ats, epoch) {
  df <- all_ats %>% 
    filter(att_slot >= epoch * slots_per_epoch & att_slot < (epoch + 1) * slots_per_epoch)
  df %>%
    pull(attesting_indices) %>%
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
      target_block_root = df$target_block_root, .before = "1") %>%
    pivot_longer(matches("[0-9]+"), names_to = "index_in_committee") %>%
    drop_na() %>%
    mutate(index_in_committee = strtoi(index_in_committee) - 1) %>%
    mutate(index_in_committee = 8 * ((index_in_committee %/% 8) + 1) - 1 - (index_in_committee %% 8))
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
  t <- GET(str_c("http://localhost:5052/eth/v1/beacon/blocks/", slot))$content %>%
    rawToChar() %>%
    fromJSON() %>%
    .$data
  
  if (is.null(t)) {
    return(NULL)
  }
  
  t <- t %>%
    .$message
  
  if (as.numeric(t$slot) != slot) {
    return(NULL)
  }
  
  return(
    tibble(
      slot = slot,
      parent_root = str_trunc(t$parent_root, 12, "left", ellipsis = ""),
      state_root = str_trunc(t$state_root, 12, "left", ellipsis = ""),
      proposer_index = as.numeric(t$proposer_index),
      graffiti = tolower(hex2string(t$body$graffiti)),
    ) %>%
      mutate(declared_client = find_client(graffiti))
  )
}

get_blocks <- function(epoch) {
  print(str_c("Getting blocks of epoch ", epoch))
  start_slot <- epoch * slots_per_epoch
  end_slot <- (epoch + 1) * slots_per_epoch - 1
  start_slot:end_slot %>%
    map(get_block_at_slot)
}