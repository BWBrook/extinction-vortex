# Cross-implementation check (run after both freezes): Astra's m0_step() on shared configs.
source("analysis/astra/m0/m0.R")
set.seed(20261009)
cfg <- list(c(0.75, 0.20, 0.4), c(0.60, 0.25, 0.5), c(0.95, 0.03, 0.3))
for (p in cfg) for (n0 in c(3, 10, 60)) {
  x <- m0_step(rep(n0, 200000), p[1], p[2], p[3])
  cat(sprintf("onestep s=%.2f f=%.2f sigma=%.1f N=%d mean=%.4f var=%.4f\n", p[1], p[2], p[3], n0, mean(x), var(x)))
}
# Selection: 200000 trajectories, 1970..1992 from 77, first recorded <= 1 at 1992
n <- rep(77, 200000); first <- rep(NA_integer_, 200000); prof <- matrix(NA, 200000, 23); prof[, 1] <- 77
for (j in 2:23) { n <- m0_step(n, 0.60, 0.25, 0.5); prof[, j] <- n
  hit <- is.na(first) & n <= 1; first[hit] <- j }
acc <- !is.na(first) & first == 23
cat(sprintf("selection acceptance=%.5f (n=%d)\n", mean(acc), sum(acc)))
cat("mean recorded count at s=1..5 among accepted:", sprintf("%.3f", colMeans(prof[acc, 22:18, drop = FALSE])), "\n")
