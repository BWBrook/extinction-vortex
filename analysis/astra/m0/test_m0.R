source("analysis/astra/m0/m0.R")
expect_error <- function(expr) stopifnot(inherits(tryCatch(force(expr), error = identity), "error"))
expect_error(m0_step(10, 1.1, 0.2, 0.1))
expect_error(m0_step(10.5, 0.6, 0.2, 0.1))
expect_error(m0_step(10, 0.6, -1, 0.1))
set.seed(640801)
stopifnot(all(m0_step(rep(0, 100), 0.8, 0.4, 0.7) == 0))
stopifnot(all(m0_step(rep(10, 100), 0.8, 0, 0.7) <= 10))
stopifnot(abs(m0_expected_multiplier(0.8, 0.2, 0) - 1) < 1e-12)
schedule <- c(2000L, 2002L, 2005L)
set.seed(640802)
gapped <- simulate_m0(20, schedule, 0.65, 0.3, 0.4)
set.seed(640802)
annual <- simulate_m0(20, 2000:2005, 0.65, 0.3, 0.4)
stopifnot(identical(gapped$latent, annual$latent), identical(gapped$census$year, schedule))
stopifnot(identical(gapped$census$count, annual$census$count[c(1, 3, 6)]))
stopifnot(matches_selection(data.frame(year = 2000:2003, count = c(4, 2, 1, 0)), 2002))
stopifnot(!matches_selection(data.frame(year = 2000:2003, count = c(4, 2, 1, 0)), 2003))
stopifnot(matches_selection(data.frame(year = c(2000, 2002), count = c(4, 1)), 2002))
# Modest synthetic invariant test; independent of empirical reconstruction.
results <- list()
k <- 0L
for (rho in c(1, 0.5)) for (n in c(1, 20, 100)) {
  k <- k + 1L
  set.seed(640810 + k)
  y <- m0_step(rep(n, 30000), 0.7, 0.25, 0.6, rho)
  expected <- n * m0_expected_multiplier(0.7, 0.25, 0.6)
  mcse <- sd(y) / sqrt(length(y))
  z <- (mean(y) - expected) / mcse
  stopifnot(all(y >= 0), all(y == round(y)), abs(z) < 5)
  results[[k]] <- data.frame(rho = rho, n = n, draws = length(y), expected = expected,
    observed = mean(y), mcse = mcse, discrepancy_mcse = z)
}
print(do.call(rbind, results), row.names = FALSE)
cat("M0 support, zero absorption, expected growth, calendar schedule and endpoint tests passed.\n")
cat("No literature prior, calibration bank, empirical p-value or production validation was run.\n")
