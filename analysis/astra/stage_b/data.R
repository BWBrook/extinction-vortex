williams_sha256 <- "fce2d8a232460b56f5566c41c03038a3f99ca978e0620a49867e5016a34df168"

sha256_file <- function(path) {
  if (nzchar(Sys.which("sha256sum"))) {
    value <- system2("sha256sum", shQuote(path), stdout = TRUE)
  } else if (nzchar(Sys.which("shasum"))) {
    value <- system2("shasum", c("-a", "256", shQuote(path)), stdout = TRUE)
  } else stop("A SHA-256 command is required")
  strsplit(value[1L], "[[:space:]]+")[[1L]][1L]
}

make_series_data <- function(year, count, population) {
  keep <- !is.na(count)
  year <- year[keep]
  count <- count[keep]
  if (!length(count) || any(!is.finite(count)) || any(count < 0) || any(count != round(count))) stop("Invalid census count")
  if (any(diff(year) <= 0)) stop("Census years must increase")
  endpoint <- which(count <= 1)[1L]
  if (is.na(endpoint) || endpoint < 2L) stop("No usable extinction endpoint")
  year <- year[seq_len(endpoint)]
  count <- count[seq_len(endpoint)]
  if (any(diff(year) != 1L)) stop("Unsupported gap: do not reinterpret multi-year changes as annual")
  raw_endpoint <- tail(count, 1L)
  adjusted <- count
  adjusted[length(count)] <- 1
  k <- seq_len(length(count) - 1L)
  growth <- data.frame(population = population, year = year[k + 1L], observation_index = k + 1L,
    s = max(year) - year[k + 1L], previous_count = adjusted[k], next_count = adjusted[k + 1L],
    growth = log(adjusted[k + 1L] / adjusted[k]))
  scaling <- data.frame(population = population, year = year[k], observation_index = k, s = max(year) - year[k],
                        count = count[k], log_count = log(count[k]))
  scaling$late <- as.integer(scaling$s <= 9)
  metadata <- data.frame(population = population, first_year = year[1L], endpoint_year = max(year),
    n_censuses = length(count), raw_endpoint = raw_endpoint,
    final_pre_endpoint = count[length(count) - 1L], n_growth = nrow(growth), n_scaling = nrow(scaling))
  list(growth = growth, scaling = scaling, metadata = metadata)
}

load_fh_data <- function(path = "data/raw/williams2021/population_data.csv") {
  digest <- sha256_file(path)
  if (!identical(digest, williams_sha256)) stop("Input SHA-256 mismatch; refusing to read")
  raw <- read.csv(path, check.names = FALSE, na.strings = c("NULL", ""))
  ids <- c(14, 15, 6, 20, 21, 10, 4, 8, 9)
  year_cols <- names(raw)[grepl("^[0-9]{4}$", names(raw))]
  series <- lapply(seq_along(ids), function(i) {
    row <- raw[raw$ID == ids[i], , drop = FALSE]
    if (nrow(row) != 1L) stop("Non-unique Williams ID")
    value <- make_series_data(as.integer(year_cols), as.numeric(row[1L, year_cols]), sprintf("FH%02d", i))
    value$metadata$williams_id <- ids[i]
    value$metadata$units <- row$Units
    value$metadata$species <- row$Binomial
    value
  })
  list(growth = do.call(rbind, lapply(series, `[[`, "growth")),
       scaling = do.call(rbind, lapply(series, `[[`, "scaling")),
       metadata = do.call(rbind, lapply(series, `[[`, "metadata")), input_sha256 = digest)
}
