# Batch T1-T4 (adopted definitions; RI primary, AR(1), marginal ML; optim, then nlminb,
# no further restarts) for many nine-population datasets.
# Input CSV columns: set, pop, year, N. Output CSV: set, T1..T4, status.
# Usage: Rscript tstats_batch.R in.csv out.csv [workers]
suppressMessages({library(nlme); library(parallel)})
args <- commandArgs(TRUE)
x <- read.csv(args[1]); workers <- if (length(args) > 2) as.integer(args[3]) else 1L

fit <- function(f, d) {
  for (opt in c("optim", "nlminb")) {
    m <- tryCatch(lme(f, random = ~ 1 | pop, data = d, method = "ML",
                      correlation = corAR1(form = ~ s | pop),
                      control = lmeControl(opt = opt, maxIter = 200, msMaxIter = 200)),
                  error = function(e) NULL)
    if (!is.null(m)) return(m)
  }
  NULL
}

tstats <- function(d) {
  g <- do.call(rbind, lapply(split(d, d$pop), function(p) {
    p <- p[order(p$year), ]; N <- p$N; N[length(N)] <- 1      # endpoint -> 1 for log growth only
    s <- max(p$year) - p$year
    keep <- diff(p$year) == 1                                  # gaps are never annualised
    data.frame(pop = p$pop[1], s = s[-1][keep], D = log(N[-1] / N[-length(N)])[keep])
  }))
  m1 <- fit(D ~ s, g); if (is.null(m1)) return(c(NA, NA, NA, NA, 1))
  g$r2 <- residuals(m1, level = 1)^2; m3 <- fit(r2 ~ s, g)
  h <- g[g$s >= 1, ]; m2 <- fit(D ~ s, h)
  t4 <- NA
  if (!is.null(m2)) { h$r2 <- residuals(m2, level = 1)^2; m4 <- fit(r2 ~ s, h); if (!is.null(m4)) t4 <- fixef(m4)[2] }
  out <- c(fixef(m1)[2], if (is.null(m2)) NA else fixef(m2)[2], if (is.null(m3)) NA else fixef(m3)[2], t4)
  c(out, as.integer(any(is.na(out))))
}

sets <- split(x, x$set)
res <- mclapply(sets, tstats, mc.cores = workers)
out <- data.frame(set = as.integer(names(sets)), do.call(rbind, res))
names(out) <- c("set", "T1", "T2", "T3", "T4", "failed")
write.csv(out, args[2], row.names = FALSE)
