library(tidyverse)
library(animation)
library(gganimate)

source(here::here("notebooks/lib.R"))

all_ats <- fread(here::here("rds_data/all_ats.csv"))
max(all_ats$slot) %/% 32

slots_per_epoch <- 32
slots_per_year <- 365.25 * 24 * 60 * 60 / 12
epochs_per_year <- slots_per_year / slots_per_epoch

chunk_size <- 100
ats_over_time <- seq(0, 20000 - chunk_size, chunk_size) %>%
  map(function(epoch) {
    print(str_c("Epoch ", epoch))
    all_ats[(att_slot >= epoch * slots_per_epoch) & (att_slot < ((epoch + chunk_size) * slots_per_epoch - 1)),] %>%
      get_exploded_ats() %>%
      .[, .(att_slot, committee_index, index_in_committee)] %>%
      unique() %>%
      merge(epoch:(epoch + chunk_size - 1) %>%
              map(get_committees) %>%
              rbindlist()) %>%
      .[, .(epoch = epoch + chunk_size, included_ats=.N), by=validator_index]
  }) %>%
  rbindlist()

cum_ats_over_time <- ats_over_time %>%
  .[, .(epoch=epoch, included_ats = included_ats, cum_included_ats = cumsum(included_ats)),
    by=.(validator_index)]

df <- seq(chunk_size, 20000, chunk_size) %>%
  map(function(current_epoch) {
    print(str_c("Epoch ", current_epoch))
    get_validators(current_epoch)[
      time_active > 0, .(validator_index, balance, time_active, activation_epoch)
    ] %>%
      merge(cum_ats_over_time[epoch==current_epoch, .(validator_index, cum_included_ats)],
            all.x = TRUE, by.x = c("validator_index"),
            by.y = c("validator_index")) %>%
      setnafill("const", fill = 0, cols = c("cum_included_ats")) %>%
      mutate(
        balance = if_else(balance < 16e9, 16e9+1, balance),
        round_balance = round(balance / (32e9)) * 32e9,
        true_rewards = balance - round_balance,
        balance_diff = true_rewards / (32e9) * 100 * epochs_per_year / time_active,
        percent_attested = cum_included_ats / time_active * 100,
        epoch = current_epoch
      )
  }) %>%
  bind_rows()

p <- ggplot(df %>%
         filter(epoch <= 20000) %>%
         filter(balance_diff < 50, balance_diff > -100) %>%
         mutate(epoch = as_factor(epoch)),
       aes(x = percent_attested, y = balance_diff, color = activation_epoch)) +
  geom_point(aes(group = epoch), alpha = 0.2) +
  scale_color_viridis_c() +
  # geom_hline(yintercept = 0, colour = "steelblue", linetype = "dashed") +
  xlab("Percent of epochs attested") +
  ylab("Annualised reward (%)") +
  labs(title = 'Epoch: {closest_state}', x = 'Percent attested', y = 'Annual reward') +
  transition_states(epoch,
                    transition_length = 0,
                    state_length = 1,
                    wrap = FALSE)

nframes <- 200
fps <- 20

anim_save("hello.gif", animation = p,
          width = 900, # 900px wide
          height = 600, # 600px high
          nframes = nframes, # 200 frames
          fps = fps)