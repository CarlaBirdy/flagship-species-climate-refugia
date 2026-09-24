
############
## Set up ##
############

# ---- Packages ----
library(terra)
library(tidyterra)
library(dplyr)
library(ggplot2)
library(viridis)
library(patchwork)
library(ggspatial)

# ---- Paths ----
dataWd <- "N:/Current-Users/Carla-Archibald/WWF/"
habWd  <- file.path(dataWd, "habitat_suit_data")

species_extents <- list(
  "Phascolarctos_cinereus"     = c(xmin = 112, xmax = 155, ymin = -45, ymax = -10), # Koala
  "Calyptorhynchus_baudinii"   = c(xmin=115, xmax=155, ymin=-40, ymax=-10), # WA cockatoo
  "Malurus_coronatus"           = c(xmin=110, xmax=155, ymin=-45, ymax=-10), # fairy wren, zoomed out
  "Pseudochirops_archeri"       = c(xmin=145, xmax=155, ymin=-20, ymax=-10), # tropical ringtail
  "Pseudochirulus_cinereus"     = c(xmin=145, xmax=155, ymin=-20, ymax=-10), # tropical ringtail
  "Hemibelideus_lemuroides"     = c(xmin=145, xmax=155, ymin=-20, ymax=-10)  # tropical ringtail
)

species_vec <- names(species_extents)


# ---- Australian shapefile ----
Aus_shp <- vect(file.path(
  dataWd,
  "state_2011_aus/STE11aAust.shp"
)) %>%
  dplyr::filter(STATE_NAME != "Other Territories")

Aus_shp_aea <- project(
  Aus_shp,
  "+proj=aea +lat_1=-18 +lat_2=-36 +lat_0=0 +lon_0=132 +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs"
)

plot(Aus_shp_aea)

terra::expanse(Aus_shp_aea, unit = "km")

################################################################################
#                         Habitat and Delta maps                               #
################################################################################

plot_species_suitability <- function(species, habWd, Aus_shp, save_plots = TRUE) {
  
  sp_dir <- file.path(habWd, species)
  
  get_one <- function(pattern) {
    f <- list.files(sp_dir, pattern = pattern, full.names = TRUE)
    if(length(f) != 1)
      stop(species, ": expected 1 file for pattern ", pattern)
    terra::rast(f)
  }
  
  # --- Load rasters ---
  r_hist <- get_one("historic_baseline_1990.*EnviroSuit.tif$")
  r_15   <- get_one("GCM-Ensembles_ssp245_2050.*EnviroSuit.tif$")
  r_20   <- get_one("GCM-Ensembles_ssp370_2050.*EnviroSuit.tif$")
  
  # CRS workaround
  crs(r_15) <- crs(r_hist)
  crs(r_20) <- crs(r_hist)
  
  # Keep first band only
  r_hist <- r_hist[[1]]
  r_15   <- r_15[[1]]
  r_20   <- r_20[[1]]
  
  # Stack suitability rasters
  r_suit <- c(r_hist, r_15, r_20)
  names(r_suit) <- c("Historic 1990", "1.5°C SSP245", "2.0°C SSP370")
  
  # --- Non-linear transform (for colour contrast) ---
  # assumes suitability scaled 0–1
  # Rescale from 0–100 to 0–1
  r_suit_01 <- r_suit / 100
  
  # Non-linear transform (emphasise high suitability)
  r_suit_nl <- r_suit_01 ^ 0.5
  
  # --- Calculate deltas ---
  delta_15 <- r_15 - r_hist
  delta_20 <- r_20 - r_hist
  
  names(delta_15) <- "Delta 1.5°C"
  names(delta_20) <- "Delta 2.0°C"
  
  r_delta <- c(delta_15, delta_20)
  
  # --- Plot extent: Australia ---
  xlims <- c(112, 155)
  ylims <- c(-44, -10)
  
  # --- Colour ramp (single-colour) ---
  suit_cols <- colorRampPalette(c("white", "#0B5D1E"))(256)
  
  # --- Plot suitability ---
  p_suit <- ggplot() +
    geom_spatraster(data = r_suit_nl) +
    geom_spatvector(
      data = Aus_shp,
      fill = NA,
      colour = "grey40",
      linewidth = 0.3
    ) +
    coord_sf(xlim = xlims, ylim = ylims, expand = FALSE) +
    facet_wrap(~lyr, ncol = 3) +
    scale_fill_gradientn(
      colours = suit_cols,
      limits  = c(0, 1),
      na.value = NA,
      name = "Habitat suitability"
    ) +
    annotation_scale(location = "bl", width_hint = 0.25) +
    annotation_north_arrow(
      location = "tl",
      style = north_arrow_fancy_orienteering
    ) +
    theme_void() +
    theme(
      legend.position = "bottom",
      strip.text = element_text(size = 26, face = "bold"),
      panel.border = element_rect(colour = "black", fill = NA, linewidth = 1)
    )
  
  # --- Plot delta ---
  p_delta <- ggplot() +
    geom_spatraster(data = r_delta) +
    geom_spatvector(
      data = Aus_shp,
      fill = NA,
      colour = "grey40",
      linewidth = 0.3
    ) +
    coord_sf(xlim = xlims, ylim = ylims, expand = FALSE) +
    facet_wrap(~lyr, ncol = 2) +
    scale_fill_gradient2(
      low = "#E6C64C",
      mid = "white",
      high = "#4C8CCA",
      midpoint = 0,
      na.value = NA,
      name = "Change in suitability"
    ) +
    annotation_scale(location = "bl", width_hint = 0.25) +
    annotation_north_arrow(
      location = "tl",
      style = north_arrow_fancy_orienteering
    ) +
    theme_void() +
    theme(
      legend.position = "bottom",
      strip.text = element_text(size = 26, face = "bold"),
      panel.border = element_rect(colour = "black", fill = NA, linewidth = 1)
    )
  
  # --- Save plots ---
  if (save_plots) {
    if (!dir.exists(sp_dir)) dir.create(sp_dir, recursive = TRUE)
    
    ggsave(
      file.path(sp_dir, paste0(species, "_raw_suitability.png")),
      p_suit, width = 12, height = 6, dpi = 300
    )
    
    ggsave(
      file.path(sp_dir, paste0(species, "_delta.png")),
      p_delta, width = 8, height = 6, dpi = 300
    )
  }
  
  list(
    raw_suitability = p_suit,
    delta = p_delta
  )
}

# --- Loop through all species ---
all_plots <- lapply(species_vec, function(sp){
  plot_species_suitability(sp, habWd, Aus_shp, save_plots = TRUE)
})
names(all_plots) <- species_vec





