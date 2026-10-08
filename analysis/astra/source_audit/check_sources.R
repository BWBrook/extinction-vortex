# Run from repo root: Rscript analysis/astra/source_audit/check_sources.R WILDDOGS_RDA NEW_OUTPUT_DIR
# MARSS URL/revision and official crane-table provenance are in the audit note.
source("analysis/astra/stage_b/data.R")
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L || dir.exists(args[2L])) stop("Supply wilddogs.rda and a new output directory")
stopifnot(sha256_file(args[1L]) == "cb6e06203eb7bcaa98a1d0bb2c1fd1aaae29690481809f5d1b8d269da32aaf87")
stopifnot(sha256_file("data/raw/williams2021/population_data.csv") == williams_sha256)
e <- new.env()
load(args[1L], envir = e)
raw <- read.csv("data/raw/williams2021/population_data.csv", check.names = FALSE, na.strings = "NULL")
dog <- data.frame(year = e$wilddogs[, "Year"], MARSS = e$wilddogs[, "Count"])
dog$Williams <- as.numeric(raw[raw$ID == 14, as.character(dog$year)])
dog$difference_if_observed <- dog$Williams - dog$MARSS
stopifnot(all(dog$difference_if_observed[!is.na(dog$MARSS)] == 0),
          identical(dog$year[is.na(dog$MARSS)], c(1971L, 1972L, 1978L)))
crane <- read.csv("analysis/astra/source_audit/crane_table1_transcription.csv")
crane$official_total <- crane$adult + crane$young
crane$Williams <- as.numeric(raw[raw$ID == 10, as.character(crane$williams_year)])
crane$difference <- crane$Williams - crane$official_total
stopifnot(all(crane$difference == 0), nrow(crane) == 18)
dir.create(args[2L], recursive = TRUE)
write.csv(dog, file.path(args[2L], "wilddog_comparison.csv"), row.names = FALSE, na = "NA")
write.csv(crane, file.path(args[2L], "crane_comparison.csv"), row.names = FALSE)
cat("Wild dog: all", sum(!is.na(dog$MARSS)), "shared observed counts match; Williams fills 3 MARSS gaps.\n")
cat("Crane: all 18 winter totals match using the winter-ending year.\n")
