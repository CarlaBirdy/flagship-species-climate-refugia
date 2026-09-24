################################################################################
#                              WWF Species SDM                                 #
#         Habitat suitability & delta maps — publication figures               #
################################################################################

# ---- Packages ----
library(terra)
library(tidyterra)
library(dplyr)
library(ggplot2)
library(patchwork)
library(ggspatial)
library(scales)
library(sf)

# ---- Paths ----
dataWd <- "N:/Current-Users/Carla-Archibald/WWF/"
habWd  <- file.path(dataWd, "habitat_suit_data")
figWd  <- file.path(dataWd, "Figures")
if (!dir.exists(figWd)) dir.create(figWd)

################################################################################
#   Species config                                                             #
################################################################################

species_config <- list(
  "Phascolarctos_cinereus" = list(
    label = "Koala"
  ),
  "Calyptorhynchus_baudinii" = list(
    label = "Baudin's black-cockatoo"
  ),
  "Malurus_coronatus" = list(
    label = "Purple-crowned fairy-wren"
  ),
  "Pseudochirops_archeri" = list(
    label = "Green ringtail possum"
  ),
  "Pseudochirulus_cinereus" = list(
    label = "Daintree River ringtail possum"
  ),
  "Hemibelideus_lemuroides" = list(
    label = "Lemuroid ringtail possum"
  )
)

species_vec <- names(species_config)

# EOO padding in degrees
EOO_PAD <- 1.5

################################################################################
#   Australian shapefile                                                       #
################################################################################

Aus_shp <- vect(file.path(dataWd, "state_2011_aus/STE11aAust.shp")) %>%
  dplyr::filter(STATE_NAME != "Other Territories")

################################################################################
#   EOO colour + label lookups                                                 #
################################################################################

eoo_colours <- c(
  "Phascolarctos_cinereus"   = "#4C8CCA",
  "Calyptorhynchus_baudinii" = "#E8A000",
  "Malurus_coronatus"        = "#2E8B57",
  "Pseudochirops_archeri"    = "#9B59B6",
  "Pseudochirulus_cinereus"  = "#E74C3C",
  "Hemibelideus_lemuroides"  = "#F39C12"
)

eoo_labels <- c(
  "Phascolarctos_cinereus"   = "Koala",
  "Calyptorhynchus_baudinii" = "Baudin's black-cockatoo",
  "Malurus_coronatus"        = "Purple-crowned fairy-wren",
  "Pseudochirops_archeri"    = "Green ringtail possum",
  "Pseudochirulus_cinereus"  = "Daintree River ringtail possum",
  "Hemibelideus_lemuroides"  = "Lemuroid ringtail possum"
)

################################################################################
#   Shared colour scales                                                       #
################################################################################

suit_cols  <- colorRampPalette(c("white", "#0B5D1E"))(256)
delta_low  <- "#E6C64C"
delta_high <- "#4C8CCA"

################################################################################
#   Helper: derive map extent from EOO shapefile + padding                    #
################################################################################

get_eoo_extent <- function(species, pad = EOO_PAD) {
  sp_dir    <- file.path(habWd, species)
  eoo_files <- list.files(sp_dir,
                          pattern     = "Extent_of_occurrence_buffered\\.shp$",
                          full.names  = TRUE,
                          ignore.case = TRUE)
  if (length(eoo_files) == 0)
    stop("No EOO shapefile found for ", species, "\n  Searched in: ", sp_dir)
  
  eoo <- vect(eoo_files[1])
  bb  <- ext(eoo)
  
  list(
    xlims = c(max(xmin(bb) - pad, 112), min(xmax(bb) + pad, 155)),
    ylims = c(max(ymin(bb) - pad, -44), min(ymax(bb) + pad, -10))
  )
}

################################################################################
#   Pre-calculate EOO extents; lock all ringtails to Daintree River extent    #
################################################################################

message("Deriving EOO-based extents...")

eoo_extents <- lapply(species_vec, function(sp) {
  ex <- get_eoo_extent(sp)
  message("  ", sp, ": x = ", round(ex$xlims[1], 1), "-",
          round(ex$xlims[2], 1), ", y = ", round(ex$ylims[1], 1),
          "-", round(ex$ylims[2], 1))
  ex
})
names(eoo_extents) <- species_vec

# Lock all three ringtails to the Daintree River ringtail extent
ringtail_species <- c("Pseudochirops_archeri",
                      "Pseudochirulus_cinereus",
                      "Hemibelideus_lemuroides")

daintree_ext <- eoo_extents[["Pseudochirulus_cinereus"]]

for (sp in ringtail_species) {
  eoo_extents[[sp]] <- daintree_ext
}

message("Ringtail extents locked to Daintree River ringtail: x = ",
        round(daintree_ext$xlims[1], 1), "-", round(daintree_ext$xlims[2], 1),
        ", y = ", round(daintree_ext$ylims[1], 1), "-",
        round(daintree_ext$ylims[2], 1))

################################################################################
#   Pre-calculate global symmetric delta range                                 #
################################################################################

message("Calculating global delta range...")

global_delta_max <- max(sapply(species_vec, function(sp) {
  sp_dir <- file.path(habWd, sp)
  get_one <- function(pat) {
    f <- list.files(sp_dir, pattern = pat, full.names = TRUE)
    terra::rast(f)[[1]]
  }
  r_hist <- get_one("historic_baseline_1990.*EnviroSuit.tif$")
  r_15   <- get_one("GCM-Ensembles_ssp245_2050.*EnviroSuit.tif$")
  r_20   <- get_one("GCM-Ensembles_ssp370_2050.*EnviroSuit.tif$")
  crs(r_15) <- crs(r_hist)
  crs(r_20) <- crs(r_hist)
  max(abs(c(
    terra::minmax(r_15 - r_hist),
    terra::minmax(r_20 - r_hist)
  )), na.rm = TRUE)
}))

message("Global delta max: ", round(global_delta_max, 1))

################################################################################
#   Data loader                                                                #
################################################################################

load_species_data <- function(species) {
  sp_dir <- file.path(habWd, species)
  
  get_one <- function(pat) {
    f <- list.files(sp_dir, pattern = pat, full.names = TRUE)
    if (length(f) != 1)
      stop(species, ": expected 1 file for '", pat, "', found ", length(f))
    terra::rast(f)[[1]]
  }
  
  r_hist <- get_one("historic_baseline_1990.*EnviroSuit.tif$")
  r_15   <- get_one("GCM-Ensembles_ssp245_2050.*EnviroSuit.tif$")
  r_20   <- get_one("GCM-Ensembles_ssp370_2050.*EnviroSuit.tif$")
  crs(r_15) <- crs(r_hist)
  crs(r_20) <- crs(r_hist)
  
  eoo_files <- list.files(sp_dir,
                          pattern     = "Extent_of_occurrence_buffered\\.shp$",
                          full.names  = TRUE,
                          ignore.case = TRUE)
  eoo <- if (length(eoo_files) > 0) vect(eoo_files[1]) else NULL
  if (is.null(eoo)) warning("No EOO shapefile found for ", species)
  
  list(r_hist = r_hist, r_15 = r_15, r_20 = r_20, eoo = eoo)
}

################################################################################
#   Shared map theme                                                           #
################################################################################

map_theme <- theme_void(base_size = 9) +
  theme(
    strip.text        = element_text(size = 8, face = "bold"),
    plot.title        = element_text(size = 9, face = "bold.italic",
                                     hjust = 0.5, margin = margin(b = 2)),
    plot.subtitle     = element_text(size = 7.5, hjust = 0.5,
                                     colour = "grey30", margin = margin(b = 3)),
    legend.position   = "bottom",
    legend.title      = element_text(size = 8, face = "bold"),
    legend.text       = element_text(size = 7),
    legend.key.width  = unit(1.6, "cm"),
    legend.key.height = unit(0.3, "cm"),
    panel.border      = element_rect(colour = "grey30", fill = NA,
                                     linewidth = 0.5),
    plot.margin       = margin(2, 2, 2, 2)
  )

################################################################################
#   Figure 1: EOO overview map                                                 #
################################################################################

build_eoo_overview <- function(species_vec, habWd, Aus_shp) {
  
  eoo_list <- lapply(species_vec, function(sp) {
    sp_dir    <- file.path(habWd, sp)
    eoo_files <- list.files(sp_dir,
                            pattern     = "Extent_of_occurrence_buffered\\.shp$",
                            full.names  = TRUE,
                            ignore.case = TRUE)
    if (length(eoo_files) == 0) {
      warning("No EOO found for ", sp)
      return(NULL)
    }
    v         <- vect(eoo_files[1])
    v$species <- sp
    v
  })
  
  eoo_list <- Filter(Negate(is.null), eoo_list)
  
  if (length(eoo_list) == 0)
    stop("No EOO shapefiles found for any species. Check folder structure.")
  
  eoo_all    <- do.call(rbind, eoo_list)
  eoo_sf     <- sf::st_as_sf(eoo_all)
  Aus_sf     <- sf::st_as_sf(Aus_shp)
  sp_in_data <- unique(eoo_sf$species)
  
  ggplot() +
    geom_sf(data = Aus_sf, fill = "grey95", colour = "grey50",
            linewidth = 0.3) +
    geom_sf(data = eoo_sf,
            aes(fill = species, colour = species),
            alpha = 0.35, linewidth = 0.4) +
    scale_fill_manual(values = eoo_colours[sp_in_data],
                      labels = eoo_labels[sp_in_data],
                      name   = NULL) +
    scale_colour_manual(values = eoo_colours[sp_in_data],
                        labels = eoo_labels[sp_in_data],
                        name   = NULL) +
    coord_sf(xlim = c(112, 155), ylim = c(-44, -10), expand = FALSE) +
    annotation_scale(location = "bl", width_hint = 0.2,
                     text_cex = 0.6, line_width = 0.5) +
    annotation_north_arrow(location = "tr", which_north = "true",
                           height = unit(0.6, "cm"), width = unit(0.6, "cm"),
                           style  = north_arrow_minimal()) +
    guides(
      fill   = guide_legend(override.aes = list(alpha = 0.6, linewidth = 0.4)),
      colour = guide_legend(override.aes = list(alpha = 0.6, linewidth = 0.4))
    ) +
    theme_void(base_size = 9) +
    theme(
      legend.position = "right",
      legend.text     = element_text(size = 8, face = "italic"),
      legend.key.size = unit(0.5, "cm"),
      panel.border    = element_rect(colour = "grey30", fill = NA,
                                     linewidth = 0.5),
      plot.margin     = margin(3, 3, 3, 3)
    )
}

################################################################################
#   SI figures: suitability maps (Historic | SSP2-4.5 | SSP3-7.0)            #
################################################################################

build_suit_panel <- function(species) {
  
  cfg <- species_config[[species]]
  dat <- load_species_data(species)
  ext <- eoo_extents[[species]]
  
  # Crop extent object for terra
  crop_ext <- ext(ext$xlims[1], ext$xlims[2], ext$ylims[1], ext$ylims[2])
  
  r_suit <- c(dat$r_hist, dat$r_15, dat$r_20)
  names(r_suit) <- c("Historic 1990",
                     "1.5\u00b0C aligned scenario (SSP2-4.5 2050)",
                     "2.0\u00b0C aligned scenario (SSP3-7.0 2050)")
  
  # Crop to EOO extent before transform — prevents geom_spatraster
  # from setting aspect ratio based on full raster extent
  r_suit    <- crop(r_suit, crop_ext)
  r_suit_nl <- (r_suit / 100) ^ 0.5
  
  ggplot() +
    geom_spatraster(data = r_suit_nl) +
    { if (!is.null(dat$eoo))
      geom_spatvector(data      = dat$eoo,
                      fill      = NA,
                      colour    = "grey20",
                      linewidth = 0.5,
                      linetype  = "dashed")
    } +
    geom_spatvector(data = Aus_shp, fill = NA,
                    colour = "grey40", linewidth = 0.25) +
    facet_wrap(~lyr, ncol = 3) +
    coord_sf(xlim = ext$xlims, ylim = ext$ylims, expand = FALSE) +
    scale_fill_gradientn(
      colours  = suit_cols,
      limits   = c(0, 1),
      na.value = NA,
      name     = "Habitat suitability",
      breaks   = c(0, 0.5, 1),
      labels   = c("0", "50", "100"),
      guide    = guide_colorbar(
        title.position = "top", title.hjust = 0.5,
        barwidth       = unit(5, "cm"), barheight = unit(0.3, "cm"),
        frame.colour   = "grey40", ticks.colour = "grey40"
      )
    ) +
    labs(title = cfg$label) +
    annotation_scale(location = "bl", width_hint = 0.25,
                     text_cex = 0.55, line_width = 0.4) +
    annotation_north_arrow(location = "tr", which_north = "true",
                           height = unit(0.6, "cm"), width = unit(0.6, "cm"),
                           style  = north_arrow_minimal()) +
    map_theme
}

################################################################################
#   Figure 2: delta maps — 6 rows x 2 cols portrait layout                   #
################################################################################

build_delta_row <- function(species, show_legend = FALSE) {
  
  cfg <- species_config[[species]]
  dat <- load_species_data(species)
  ext <- eoo_extents[[species]]
  
  # Crop extent object for terra
  crop_ext <- ext(ext$xlims[1], ext$xlims[2], ext$ylims[1], ext$ylims[2])
  
  # Compute and crop deltas to EOO extent before plotting
  delta_15 <- crop(dat$r_15 - dat$r_hist, crop_ext)
  delta_20 <- crop(dat$r_20 - dat$r_hist, crop_ext)
  
  make_panel <- function(r_plot, scenario_label, show_scalebar,
                         show_north, show_sp_title) {
    ggplot() +
      geom_spatraster(data = r_plot) +
      { if (!is.null(dat$eoo))
        geom_spatvector(data      = dat$eoo,
                        fill      = NA,
                        colour    = "grey20",
                        linewidth = 0.45,
                        linetype  = "dashed")
      } +
      geom_spatvector(data = Aus_shp, fill = NA,
                      colour = "grey40", linewidth = 0.2) +
      coord_sf(xlim = ext$xlims, ylim = ext$ylims, expand = FALSE) +
      scale_fill_gradient2(
        low      = delta_low,
        mid      = "white",
        high     = delta_high,
        midpoint = 0,
        limits   = c(-global_delta_max, global_delta_max),
        na.value = NA,
        name     = "Change in suitability (%)",
        guide    = if (show_legend)
          guide_colorbar(
            title.position = "top", title.hjust = 0.5,
            barwidth       = unit(5, "cm"), barheight = unit(0.3, "cm"),
            frame.colour   = "grey40", ticks.colour = "grey40"
          )
        else "none"
      ) +
      labs(
        title    = if (show_sp_title) cfg$label else NULL,
        subtitle = scenario_label
      ) +
      { if (show_scalebar)
        annotation_scale(location = "bl", width_hint = 0.25,
                         text_cex = 0.55, line_width = 0.4)
      } +
      { if (show_north)
        annotation_north_arrow(location = "tr", which_north = "true",
                               height = unit(0.5, "cm"), width = unit(0.5, "cm"),
                               style  = north_arrow_minimal())
      } +
      map_theme
  }
  
  is_first <- species == species_vec[1]
  is_last  <- species == species_vec[length(species_vec)]
  
  p_left  <- make_panel(delta_15,
                        "1.5\u00b0C aligned scenario (SSP2-4.5 2050)",
                        show_scalebar = is_last,
                        show_north    = is_first,
                        show_sp_title = TRUE)
  
  p_right <- make_panel(delta_20,
                        "2.0\u00b0C aligned scenario (SSP3-7.0 2050)",
                        show_scalebar = is_last,
                        show_north    = FALSE,
                        show_sp_title = FALSE)
  
  p_left + p_right +
    plot_layout(ncol = 2, widths = c(1, 1))
}

################################################################################
#   Assemble Figure 2                                                          #
################################################################################

assemble_figure2 <- function() {
  
  message("Building Figure 2 rows...")
  
  row_list <- lapply(seq_along(species_vec), function(i) {
    sp  <- species_vec[i]
    message("  Row ", i, ": ", sp)
    show_leg <- (i == length(species_vec))
    build_delta_row(sp, show_legend = show_leg)
  })
  
  wrap_plots(row_list, ncol = 1) +
    plot_annotation(
      tag_levels = "a",
      tag_prefix = "(",
      tag_suffix = ")",
      theme = theme(plot.tag = element_text(size = 7.5, face = "bold"))
    )
}

################################################################################
#   Build & save all figures                                                   #
################################################################################

# ---- Verify EOO files ----
message("\nVerifying EOO files...")
for (sp in species_vec) {
  f <- list.files(file.path(habWd, sp),
                  pattern     = "Extent_of_occurrence_buffered\\.shp$",
                  full.names  = FALSE,
                  ignore.case = TRUE)
  cat("  ", sp, "->", if (length(f) > 0) f else "NOT FOUND", "\n")
}

# ---- Figure 1: EOO overview ----
message("\nBuilding Figure 1 (EOO overview)...")

p_overview <- build_eoo_overview(species_vec, habWd, Aus_shp)

ggsave(
  file.path(figWd, "Figure1_EOO_overview.pdf"),
  plot   = p_overview,
  width  = 130,
  height = 110,
  units  = "mm",
  dpi    = 300
)
message("Saved Figure 1")

# ---- Figure 2: delta grid ----
fig2 <- assemble_figure2()

ggsave(
  file.path(figWd, "Figure2_delta_grid.pdf"),
  plot   = fig2,
  width  = 180,
  height = 285,
  units  = "mm",
  dpi    = 300
)
message("Saved Figure 2")

# ---- SI figures: suitability per species ----
message("\nBuilding SI suitability figures...")

for (sp in species_vec) {
  message("  ", sp)
  p <- build_suit_panel(sp)
  ggsave(
    file.path(figWd, paste0("FigureS_suit_", sp, ".pdf")),
    plot   = p,
    width  = 180,
    height = 80,
    units  = "mm",
    dpi    = 300
  )
}

message("\nAll figures saved to: ", figWd)