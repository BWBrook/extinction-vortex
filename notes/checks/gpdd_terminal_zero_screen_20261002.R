# Archive of the GPDD terminal-zero screen Fable ran on 2 October 2026 (exposure
# log E05). Reconstructed verbatim from the session transcript; NOT re-run on
# 5 October. The recorded output (2 Oct) was: 531 series end in >=1 terminal zero;
# 397 have >=10 positive counts before the terminal zeros (349 with >=15); of the
# 397, 314 Insecta, 27 Osteichthyes, 22 Mammalia, 15 Aves, 8 Bacillariophyceae,
# 5 Angiospermopsida (Monocotyledonae), 4 Crustacea, 1 Chondrichthyes, 1 Unknown.
# This is an outcome-selected aggregate (selection on terminal zeros).
suppressMessages(library(rgpdd))
d <- gpdd_data; m <- gpdd_main; tx <- gpdd_taxon
d <- d[order(d$MainID, d$SeriesStep), ]
s <- split(d$Population, d$MainID)
last0 <- sapply(s, function(x) { x <- x[!is.na(x)]; length(x) > 0 && tail(x, 1) == 0 })
nz_before <- sapply(s, function(x) {
  x <- x[!is.na(x)]; k <- length(x); if (k < 2 || x[k] != 0) return(0L)
  r <- rle(x == 0); lr <- tail(r$lengths, 1); sum(x[seq_len(k - lr)] > 0)
})
cat("series ending in >=1 terminal zero:", sum(last0), "\n")
cat("  ... with >=10 positive counts before terminal zeros:", sum(nz_before >= 10), "\n")
cat("  ... with >=15 positive counts before terminal zeros:", sum(nz_before >= 15), "\n")
ids <- as.integer(names(s))[nz_before >= 10]
mm <- merge(m[m$MainID %in% ids, ], tx[, c("TaxonID", "TaxonomicClass", "TaxonName")], by = "TaxonID")
print(sort(table(mm$TaxonomicClass), decreasing = TRUE))
print(table(mm$Reliability))
print(head(sort(table(mm$SamplingUnits), decreasing = TRUE), 8))
