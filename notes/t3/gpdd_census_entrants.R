# T3 feasibility count: GPDD whole-population census series that enter a
# small-population state (first census below N* after a census >= N*), with the
# number of follow-up observations available. Post-entry values and fates are
# deliberately not inspected (forward-design outcomes remain unexamined).
# Run: Rscript notes/t3/gpdd_census_entrants.R   (needs the rgpdd package)
suppressMessages(library(rgpdd))
m <- merge(gpdd_main, gpdd_taxon[, c("TaxonID", "TaxonomicClass")], by = "TaxonID")
m$TaxonomicClass <- as.character(m$TaxonomicClass)
m$SamplingUnits <- as.character(m$SamplingUnits)
cen <- m[as.character(m$SamplingEffort) %in% c("Census", "Census (estimated)"), ]
cat("census series:", nrow(cen), "\n"); print(table(cen$TaxonomicClass))
d <- gpdd_data[gpdd_data$MainID %in% cen$MainID, ]
d <- d[order(d$MainID, d$SampleYear), ]
res <- do.call(rbind, lapply(split(d, d$MainID), function(s) {
  x <- s$PopulationUntransformed; if (all(is.na(x))) x <- s$Population
  x <- x[!is.na(x)]
  out <- c(MainID = s$MainID[1])
  for (th in c(20, 50, 100)) {
    above <- which(x >= th); entry <- NA
    if (length(above)) { cand <- which(x < th & seq_along(x) > min(above)); if (length(cand)) entry <- min(cand) }
    out[paste0("fu", th)] <- if (is.na(entry)) 0 else length(x) - entry
  }
  out
}))
res <- merge(as.data.frame(res), cen[, c("MainID", "TaxonomicClass", "SamplingUnits", "Reliability")], by = "MainID")
for (th in c(20, 50, 100)) {
  f <- res[[paste0("fu", th)]]
  cat(sprintf("N*=%3d: entrants with >=1 / >=5 / >=10 follow-up obs: %d / %d / %d\n",
              th, sum(f >= 1), sum(f >= 5), sum(f >= 10)))
}
e <- res[res$fu50 >= 5, ]
cat("\nN*=50, >=5 follow-up, by class:\n"); print(table(e$TaxonomicClass))
cat("by units:\n"); print(sort(table(e$SamplingUnits), decreasing = TRUE))
