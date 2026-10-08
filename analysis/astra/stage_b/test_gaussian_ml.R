source("analysis/astra/stage_b/gaussian_ml.R")
source("analysis/astra/stage_b/data.R")
expect_error <- function(expr) stopifnot(inherits(tryCatch(force(expr), error = identity), "error"))

# Endpoint rule and the final transition's time index, including observed N=1.
series <- make_series_data(2000:2004, c(8, 4, 2, 1, 0), "toy")
stopifnot(identical(series$growth$s, c(2L, 1L, 0L)), nrow(series$scaling) == 3,
          series$metadata$endpoint_year == 2003, series$metadata$final_pre_endpoint == 2)
zero <- make_series_data(2000:2003, c(8, 4, 2, 0), "toy")
stopifnot(identical(series$growth$growth, zero$growth$growth))
expect_error(make_series_data(c(2000, 2002, 2003), c(8, 4, 0), "gap"))
expect_error(make_series_data(2000:2002, c(8, 4, 2), "unextinct"))

# Profile objective checked against an independently assembled dense Gaussian.
x <- c(-1, 0, 2, -2, 1, 3)
y <- c(1.2, 0.3, 2.1, -1.1, 2.3, 4.0)
X <- cbind(1, x)
Z <- X
blocks <- lapply(list(1:3, 4:6), function(j) list(y = y[j], X = X[j, ], Z = Z[j, ], time = c(1, 2, 4)))
theta <- c(log(0.3), -0.15, log(0.2), atanh(-0.25))
p <- gaussian_profile(theta, blocks, 2L, TRUE, TRUE)
L <- matrix(c(0.3, -0.15, 0, 0.2), 2, 2)
H <- L %*% t(L)
W <- matrix(0, 6, 6)
for (j in list(1:3, 4:6)) W[j, j] <- (-0.25)^abs(outer(c(1, 2, 4), c(1, 2, 4), "-")) + Z[j, ] %*% H %*% t(Z[j, ])
Wi <- solve(W)
beta <- solve(t(X) %*% Wi %*% X, t(X) %*% Wi %*% y)
e <- y - X %*% beta
s2 <- drop(t(e) %*% Wi %*% e) / length(y)
nll <- (length(y) * (log(2 * pi) + 1 + log(s2)) + as.numeric(determinant(W, logarithm = TRUE)$modulus)) / 2
stopifnot(max(abs(p$beta - beta)) < 1e-11, abs(p$sigma2 - s2) < 1e-11, abs(p$nll - nll) < 1e-10)

# A synthetic fit is independently checked against nlme ML, not peer code.
if (!requireNamespace("nlme", quietly = TRUE)) stop("nlme is required for the synthetic cross-check")
set.seed(640803)
dat <- expand.grid(year = 1:9, population = sprintf("p%02d", 1:12))
dat$x <- rep(seq(-1, 1, length.out = 9), 12)
u <- rnorm(12, 0, 0.8)
v <- rnorm(12, 0, 0.5)
err <- as.vector(replicate(12, as.numeric(arima.sim(list(ar = 0.3), n = 9, sd = 0.5))))
dat$y <- 1.2 + 0.7 * dat$x + rep(u, each = 9) + rep(v, each = 9) * dat$x + err
for (random in c("intercept", "intercept_slope")) {
  fit <- fit_gaussian_ml(dat, "y", ~x, "x", random, TRUE)
  ref <- nlme::lme(y ~ x, data = dat, random = if (random == "intercept") ~1 | population else ~x | population,
                   correlation = nlme::corAR1(form = ~year | population), method = "ML",
                   control = nlme::lmeControl(msMaxIter = 500, opt = "optim"))
  stopifnot(fit$diagnostics$convergence == 0L,
    max(abs(fit$beta - nlme::fixef(ref))) < 2e-4,
    abs(-fit$nll - as.numeric(logLik(ref))) < 2e-4,
    max(abs(fit$residual_conditional - residuals(ref, level = 1, type = "response"))) < 2e-3,
    max(abs(fit$random_effects - as.matrix(nlme::ranef(ref)))) < 2e-3)
  cat(random, "synthetic ML logLik difference:", -fit$nll - as.numeric(logLik(ref)), "\n")
}
cat("Dense likelihood, endpoint/time indexing, synthetic ML, residual and EB tests passed.\n")
