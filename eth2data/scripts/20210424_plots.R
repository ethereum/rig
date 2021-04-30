### COLLECTING DATA

### Initial collection

start_epoch <- 32280
end_epoch <- 32320

new_epochs <- start_epoch:end_epoch %>%
  map(function(epoch) {
    get_blocks_and_attestations(epoch)
  }) %>%
  purrr::transpose() %>%
  map(rbindlist)

new_bxs <- copy(new_epochs$block)
new_bxs[, declared_client := find_client(graffiti)]
new_ats <- copy(new_epochs$attestations)
new_committees <- start_epoch:end_epoch %>%
  map(get_committees) %>%
  rbindlist()
block_root_at_slot <- get_block_root_at_slot(new_bxs)
get_correctness_data(new_ats, block_root_at_slot)
first_possible_inclusion_slot <- get_first_possible_inclusion_slot(new_bxs)
new_val_series <- get_stats_per_val(
  new_ats[att_slot >= 32290 * slots_per_epoch & att_slot < end_epoch * slots_per_epoch],
  block_root_at_slot, first_possible_inclusion_slot,
  committees = new_committees, chunk_size = 1)
new_stats_per_slot <- get_stats_per_slot(
  new_ats[att_slot >= (start_epoch-1) * slots_per_epoch & att_slot < end_epoch * slots_per_epoch],
  new_committees)

new_bxs %>% fwrite(here::here("data/prysmcrash/all_bxs.csv"))
new_ats %>% fwrite(here::here("data/prysmcrash/all_ats.csv"))
new_committees %>% fwrite(here::here("data/prysmcrash/committees.csv"))
new_val_series %>% fwrite(here::here("data/prysmcrash/val_series.csv"))
new_stats_per_slot %>% fwrite(here::here("data/prysmcrash/stats_per_slot.csv"))

### Update

start_epoch <- 32321
end_epoch <- 32330

all_bxs <- fread(here::here("data/prysmcrash/all_bxs.csv"))
all_ats <- fread(here::here("data/prysmcrash/all_ats.csv"))
committees <- fread(here::here("data/prysmcrash/committees.csv"))
val_series <- fread(here::here("data/prysmcrash/val_series.csv"))
stats_per_slot <- fread(here::here("data/prysmcrash/stats_per_slot.csv"))

bxs_and_ats <- start_epoch:end_epoch %>%
  map(get_blocks_and_attestations) %>%
  purrr::transpose() %>%
  map(rbindlist)

new_bxs <- copy(bxs_and_ats$block)
new_bxs[, declared_client := find_client(graffiti)]
list(all_bxs, new_bxs) %>% rbindlist() %>% fwrite(here::here("data/prysmcrash/all_bxs.csv"))
rm(new_bxs)

list(all_ats, bxs_and_ats$attestations) %>% rbindlist() %>% fwrite(here::here("data/prysmcrash/all_ats.csv"))
rm(bxs_and_ats)

new_committees <- start_epoch:end_epoch %>%
  map(get_committees) %>%
  rbindlist()
list(committees, new_committees) %>% rbindlist() %>% fwrite(here::here("data/prysmcrash/committees.csv"))
rm(new_committees)

all_bxs <- fread(here::here("data/prysmcrash/all_bxs.csv"))
block_root_at_slot <- get_block_root_at_slot(all_bxs)
all_ats <- fread(here::here("data/prysmcrash/all_ats.csv"))
committees <- fread(here::here("data/prysmcrash/committees.csv"))
get_correctness_data(all_ats, block_root_at_slot)
first_possible_inclusion_slot <- get_first_possible_inclusion_slot(all_bxs)

new_val_series <- get_stats_per_val(
  all_ats[att_slot >= (start_epoch-1) * slots_per_epoch & att_slot < end_epoch * slots_per_epoch],
  block_root_at_slot, first_possible_inclusion_slot,
  committees = committees, chunk_size = 1)

list(val_series, new_val_series) %>%
  rbindlist() %>%
  fwrite(here::here("data/prysmcrash/val_series.csv"))
rm(new_val_series)

new_stats_per_slot <- get_stats_per_slot(
  all_ats[att_slot >= (start_epoch-1) * slots_per_epoch & att_slot < end_epoch * slots_per_epoch],
  committees)
list(stats_per_slot, new_stats_per_slot) %>% rbindlist() %>% fwrite(here::here("data/prysmcrash/stats_per_slot.csv"))
rm(new_stats_per_slot)

### PLOTS

client_colours <- c("#000011", "#ff9a02", "#eb4a9b", "#7dc19e", "grey", "red")
myred <- "#F05431"
myyellow <- "#FED152"
mygreen <- "#BFCE80"

newtheme <- theme_grey() + theme(
  axis.text = element_text(size = 9),
  axis.title = element_text(size = 12),
  axis.line = element_line(colour = "#000000"),
  panel.grid.major.y = element_line(colour="#bbbbbb", size=0.1),
  panel.grid.major.x = element_blank(),
  panel.grid.minor = element_blank(),
  panel.background = element_blank(),
  legend.title = element_text(size = 12),
  legend.text = element_text(size = 10),
  legend.box.background = element_blank(),
  legend.key = element_blank(),
  strip.text.x = element_text(size = 10),
  strip.background = element_rect(fill = "white")
)
theme_set(newtheme)

start_epoch <- 32280
end_epoch <- 32320
all_bxs <- fread(here::here("data/prysmcrash/all_bxs.csv"))
all_slots <- data.table(slot = (start_epoch*32):(end_epoch*32+31))
all_bxs <- new_bxs[all_slots, on="slot", nomatch="unproposed"]
all_bxs[, epoch := slot %/% 32]

### Blocks per client plot
all_bxs[, .(num_blocks = .N), by=.(epoch, declared_client)] %>%
  ggplot() +
  geom_col(aes(x = epoch, y = num_blocks, group=declared_client, fill=declared_client),
           position = position_dodge()) +
  facet_wrap(vars(declared_client)) +
  scale_fill_manual(values = client_colours)

### Inclusion delay plot
val_series <- fread(here::here("data/prysmcrash/val_series.csv"))
val_series[epoch > 32280, .(inclusion_delay = mean(inclusion_delay, na.rm = TRUE),
                                inclusion_delay_by_block = mean(inclusion_delay_by_block, na.rm = TRUE)), by=epoch] %>%
  ggplot() +
  geom_line(aes(x = epoch, y = inclusion_delay), colour=myred) +
  geom_line(aes(x = epoch, y = inclusion_delay_by_block), colour=mygreen)

### ETH lost

balances <- 32295:32325 %>%
  map(get_balances_active_validators) %>%
  rbindlist()

balances %>% fwrite(here::here("data/prysmcrash/balances.csv"))

diff_balances <- balances %>%
  group_by(validator_index) %>%
  mutate(epoch = 32294 + row_number(), previous_balance = lag(balance), diff = balance - previous_balance)

diff_per_epoch <- diff_balances %>% group_by(epoch) %>%
  summarise(total_diff = sum(diff) / 1e9)

diff_per_epoch %>%
  ggplot() +
  geom_col(aes(x = epoch, y = total_diff), fill = mygreen)

expected_diff <- diff_per_epoch %>%
  filter(epoch < 32303) %>%
  pull(total_diff) %>%
  mean(., na.rm = TRUE)

eth_lost <- diff_per_epoch %>%
  mutate(eth_lost = expected_diff - total_diff) %>%
  filter(epoch >= 32303, epoch <= 32322) %>%
  pull(eth_lost) %>%
  sum()