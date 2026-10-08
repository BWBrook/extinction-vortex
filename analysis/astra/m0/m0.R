# Unstructured annual demographic null from protocol 0.3, section 3.1.
# Here survival is the survival probability of an individual in the model's
# census class. It is not automatically an adult-survival parameter when the
# observed census includes other ages. Empirical unit mappings remain open.

validate_m0 <- function(n, survival, recruitment, sigma, rho) {
  scalar <- c(survival, recruitment, sigma, rho)
  if (length(scalar) != 4L || any(!is.finite(scalar))) stop("Finite scalar parameters required")
  if (survival <= 0 || survival >= 1 || recruitment < 0 || sigma < 0 || abs(rho) > 1) stop("Parameters outside M0 support")
  if (!length(n) || any(!is.finite(n)) || any(n < 0) || any(n != round(n)) || any(n > 2^53)) stop("Invalid integer population size")
  invisible(TRUE)
}

m0_step <- function(n, survival, recruitment, sigma, rho = 1) {
  validate_m0(n, survival, recruitment, sigma, rho)
  z_survival <- rnorm(length(n))
  z_recruitment <- if (rho == 1) z_survival else rho * z_survival + sqrt(1 - rho^2) * rnorm(length(n))
  survival_t <- plogis(qlogis(survival) + sigma * z_survival)
  recruitment_t <- if (recruitment == 0) rep(0, length(n)) else recruitment * exp(sigma * z_recruitment - sigma^2 / 2)
  rate <- n * recruitment_t
  if (any(!is.finite(rate))) stop("Recruitment overflow; trajectory is not silently capped")
  next_n <- rbinom(length(n), n, survival_t) + rpois(length(n), rate)
  if (any(!is.finite(next_n)) || any(next_n > 2^53)) stop("Population overflow; trajectory is not silently capped")
  next_n
}

m0_expected_multiplier <- function(survival, recruitment, sigma) {
  validate_m0(1, survival, recruitment, sigma, 1)
  es <- integrate(function(z) plogis(qlogis(survival) + sigma * z) * dnorm(z),
                  -Inf, Inf, rel.tol = 1e-10)$value
  es + recruitment
}

simulate_m0 <- function(n_initial, census_years, survival, recruitment, sigma, rho = 1) {
  validate_m0(n_initial, survival, recruitment, sigma, rho)
  if (length(n_initial) != 1L || !length(census_years) || any(!is.finite(census_years)) ||
      any(census_years != round(census_years)) || any(diff(census_years) <= 0)) stop("Invalid initial count or census schedule")
  years <- seq.int(census_years[1L], tail(census_years, 1L))
  path <- numeric(length(years))
  path[1L] <- n_initial
  if (length(years) > 1L) for (t in 2:length(years)) path[t] <- m0_step(path[t - 1L], survival, recruitment, sigma, rho)
  census <- data.frame(year = census_years, count = path[match(census_years, years)])
  list(census = census, latent = data.frame(year = years, count = path))
}

first_rule_e <- function(census, threshold = 1) {
  if (!is.finite(threshold) || length(threshold) != 1L || threshold < 0 || anyNA(census$count)) stop("Invalid rule E input")
  index <- which(census$count <= threshold)[1L]
  if (is.na(index)) return(NA_integer_)
  census$year[index]
}

matches_selection <- function(census, extinction_year, threshold = 1) {
  # This is first crossing at a RECORDED census, not first latent-year crossing.
  # A transient unobserved N = 1 need not make a gapped schedule fail selection.
  observed <- first_rule_e(census, threshold)
  !is.na(observed) && observed == extinction_year
}
