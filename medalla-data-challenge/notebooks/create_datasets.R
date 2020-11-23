library(tidyverse)
library(here)
library(data.table)

options(dplyr.summarise.inform=F)

source(here::here("notebooks/lib.R"))
source(here::here("notebooks/pw.R"))

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

# Inclusion delay histogram

batch_ops_ats(function(df) {
  df %>%
    .[, .(inclusion_delay=min_inclusion_slot-att_slot)] %>%
    .[, .(count=.N), by=inclusion_delay]
}) %>%
  .[, .(count=sum(count)), by=inclusion_delay] %>%
  fwrite(here::here("rds_data/inclusion_delay_hist.csv"))
  
  
  
  