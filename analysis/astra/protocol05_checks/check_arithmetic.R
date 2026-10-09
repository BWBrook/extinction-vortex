# Deterministic protocol-review calculations, not empirical vortex tests.
# Run from the repository root: Rscript analysis/astra/protocol05_checks/check_arithmetic.R
options(width = 150, digits = 10)
cat("Reviewed source commit: 9e597d9d0b86bdca580bcc1d142f2533237e4c36\n")
cat("R: ", R.version.string, "\n", sep = "")

n <- 2000L
threshold <- 0.01
count_gap <- floor(threshold * (n + 1)) + 1L
cat("\nIndependent equal-probability binomial test references; count gap >=", count_gap, "\n")
probability <- function(p) {
  k <- 0:n
  2 * sum(dbinom(k, n, p) * pbinom(k - count_gap, n, p))
}
p <- c(0.05, 0.25, 0.5)
print(data.frame(true_tail_probability = p,
                 probability_abs_p_difference_gt_001 = vapply(p, probability, numeric(1))),
      row.names = FALSE)
cat("These are conditional examples with fixed true tail probabilities, not an overall null rejection rate.\n")
cat("Training/covariance estimation and actual bank differences are omitted.\n")
cat("\nZero failures in 20 trials: one-sided exact 95% upper bound =",
    1 - 0.05^(1 / 20), "\n")

archive <- "analysis/fable/calibration/bank_catastrophe_scan.txt"
rows <- strsplit(trimws(readLines(archive)[-(1:2)]), "[[:space:]]+")
bank <- do.call(rbind, lapply(rows, function(x) {
  accepted <- as.numeric(x[2])
  J_scan <- as.numeric(x[9])
  hits <- seq_len(accepted)
  # Recover hits only if both independently rounded archive fields agree.
  compatible <- hits[sprintf("%.4f", hits / accepted) == x[8] &
                       signif(2000 * 2e6 / hits, 3) == J_scan]
  data.frame(population = x[1], accepted = accepted,
             raw_draws_3J = 3 * J_scan,
             expected_selected_3J = 3 * J_scan * accepted / 2e6,
             exceeds_1e8_cap = 3 * J_scan > 1e8,
             misses_2e5_selected = 3 * J_scan * accepted / 2e6 < 2e5,
             recovered_joint_hits = if (length(compatible) == 1) compatible else NA_integer_)
}))
cat("\nBank-size arithmetic from rounded archived requirements; 2,000,000 raw draws each:\n")
print(bank, row.names = FALSE)
cat("\nOne-bank estimator subtotal (core-hours):", 7000 * 4000 * 0.15 / 3600, "\n")
cat("Ideal wall-hours at 60 fully occupied cores:", 7000 * 4000 * 0.15 / 3600 / 60, "\n")
cat("Excludes second-bank repetition, calibration, fallback fitting, I/O and parallel overhead.\n")
