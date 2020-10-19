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

capture_committee <- function(df) {
  df %>%
    pull(f_committee) %>%
    str_remove_all("\\{|\\}") %>%
    str_split(",") %>%
    plyr::ldply(rbind) %>%
    add_column(slot = df$f_slot) %>%
    mutate(committee_index = row_number() - 1) %>%
    pivot_longer(matches("[0-9]+"), names_to = "index_in_committee", values_to = "validator_index") %>%
    mutate(index_in_committee = strtoi(index_in_committee) - 1,
           validator_index = strtoi(validator_index),
           slot = as.numeric(slot),
           epoch = slot %/% slots_per_epoch) %>%
    rename(att_slot = slot) %>%
    group_by(epoch, att_slot) %>%
    mutate(committee_index = committee_index - min(committee_index)) %>%
    filter(!is.na(validator_index)) %>%
    ungroup()
}