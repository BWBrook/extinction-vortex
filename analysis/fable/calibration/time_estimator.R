# Time the primary (RI, AR(1), marginal ML) T1-T4 computation on synthetic nine-population
# datasets, using the adopted definitions: T1 slope of D on s; T2 refit on s >= 1;
# T3 slope of squared conditional residuals of T1 on s; T4 refit mean on s >= 1, then
# squared conditional residuals on s. Synthetic data only.
suppressMessages(library(nlme))
args <- commandArgs(TRUE); x <- read.csv(args[1])
ctl <- lmeControl(opt = "optim", maxIter = 200, msMaxIter = 200)
fit <- function(f, d) tryCatch(lme(f, random = ~ 1 | pop, data = d, method = "ML",
                                   correlation = corAR1(form = ~ s | pop), control = ctl), error = function(e) NULL)
tstats <- function(d) {
  g <- do.call(rbind, lapply(split(d, d$pop), function(p) {
    p <- p[order(p$year), ]; N <- p$N; N[length(N)] <- 1        # endpoint replaced by one
    s <- max(p$year) - p$year
    data.frame(pop = p$pop[1], s = s[-1], D = log(N[-1] / N[-length(N)]))   # transition into s
  }))
  m1 <- fit(D ~ s, g); if (is.null(m1)) return(rep(NA, 4))
  g$r2 <- residuals(m1, level = 1)^2
  m3 <- fit(r2 ~ s, g)
  h <- g[g$s >= 1, ]; m2 <- fit(D ~ s, h); if (is.null(m2)) return(c(fixef(m1)[2], NA, NA, NA))
  h$r2 <- residuals(m2, level = 1)^2; m4 <- fit(r2 ~ s, h)
  c(fixef(m1)[2], fixef(m2)[2], if (is.null(m3)) NA else fixef(m3)[2], if (is.null(m4)) NA else fixef(m4)[2])
}
t0 <- proc.time()[3]
res <- t(sapply(split(x, x$set), tstats))
el <- proc.time()[3] - t0
cat(sprintf("datasets: %d  elapsed: %.1f s  per dataset (4 statistics, 4 fits): %.2f s  failures: %d\n",
            nrow(res), el, el / nrow(res), sum(!complete.cases(res))))
print(round(head(res, 5), 4))
