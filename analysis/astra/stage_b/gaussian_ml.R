# Gaussian marginal ML, implemented without nlme or Fable's implementation.
# V_i = sigma^2 (R_i + Z_i H Z_i'), H = L L'. beta and sigma^2 are profiled.

chol_solve <- function(U, b) backsolve(U, forwardsolve(t(U), b))

covariance_parameters <- function(theta, q, ar) {
  if (q == 1L) {
    L <- matrix(exp(theta[1L]), 1L, 1L)
  } else {
    L <- matrix(c(exp(theta[1L]), theta[2L], 0, exp(theta[3L])), 2L, 2L)
  }
  list(H = tcrossprod(L), phi = if (ar) tanh(tail(theta, 1L)) else 0)
}

gaussian_profile <- function(theta, blocks, q, ar, details = FALSE) {
  pars <- covariance_parameters(theta, q, ar)
  p <- ncol(blocks[[1L]]$X)
  XX <- matrix(0, p, p)
  Xy <- numeric(p)
  logdet <- 0
  n <- 0L
  factors <- vector("list", length(blocks))
  for (i in seq_along(blocks)) {
    b <- blocks[[i]]
    R <- if (ar) pars$phi ^ abs(outer(b$time, b$time, "-")) else diag(length(b$y))
    U <- chol(R + b$Z %*% pars$H %*% t(b$Z))
    wx <- forwardsolve(t(U), b$X)
    wy <- forwardsolve(t(U), b$y)
    XX <- XX + crossprod(wx)
    Xy <- Xy + drop(crossprod(wx, wy))
    logdet <- logdet + 2 * sum(log(diag(U)))
    n <- n + length(b$y)
    factors[[i]] <- U
  }
  C <- chol(XX)
  beta <- drop(chol_solve(C, Xy))
  rss <- 0
  for (i in seq_along(blocks)) {
    e <- blocks[[i]]$y - drop(blocks[[i]]$X %*% beta)
    rss <- rss + sum(forwardsolve(t(factors[[i]]), e)^2)
  }
  sigma2 <- rss / n
  if (!is.finite(sigma2) || sigma2 <= 0) stop("Nonpositive residual ML variance")
  nll <- (n * (log(2 * pi) + 1 + log(sigma2)) + logdet) / 2
  if (!details) return(nll)
  list(nll = nll, beta = beta, sigma2 = sigma2, H = pars$H, phi = pars$phi,
       vcov = sigma2 * chol_solve(C, diag(p)), factors = factors, n = n)
}

fit_gaussian_ml <- function(data, response, fixed, random_x, random = "intercept_slope",
                            ar = TRUE, maxit = 1500L) {
  stopifnot(random %in% c("intercept", "intercept_slope"))
  X <- model.matrix(fixed, data)
  y <- data[[response]]
  x <- data[[random_x]]
  group <- as.character(data$population)
  time <- data$year
  if (anyNA(c(y, X, x, time)) || any(!is.finite(c(y, X, x, time)))) stop("Nonfinite model input")
  if (any(time != round(time))) stop("AR(1) time must be integer calendar years")
  if (qr(X)$rank != ncol(X)) stop("Fixed-effect design is rank deficient")
  if (anyDuplicated(paste(group, time, sep = ":"))) stop("Duplicate population/year")
  q <- if (random == "intercept") 1L else 2L
  center <- mean(x)
  scale <- sd(x)
  if (q == 2L && (!is.finite(scale) || scale <= 0)) stop("Constant random slope predictor")
  Z <- if (q == 1L) matrix(1, nrow(data), 1L) else cbind(1, (x - center) / scale)
  index <- split(seq_len(nrow(data)), group)
  blocks <- lapply(index, function(j) list(y = y[j], X = X[j, , drop = FALSE],
                                         Z = Z[j, , drop = FALSE], time = time[j]))
  lower <- if (q == 1L) -12 else c(-12, -40, -12)
  upper <- if (q == 1L) 8 else c(8, 40, 8)
  if (ar) { lower <- c(lower, -7); upper <- c(upper, 7) }
  # Fixed starts, never set from published or peer fitted coefficients.
  sd_starts <- c(0.05, 0.5, 2)
  phi_starts <- if (ar) c(-0.35, 0.35, 0.85) else 0
  starts <- lapply(seq_along(sd_starts), function(k) {
    t <- if (q == 1L) log(sd_starts[k]) else c(log(sd_starts[k]), 0, log(sd_starts[k]))
    if (ar) c(t, atanh(phi_starts[k])) else t
  })
  objective <- function(theta) tryCatch(gaussian_profile(theta, blocks, q, ar),
                                       error = function(e) 1e100)
  attempts <- lapply(seq_along(starts), function(k) {
    tryCatch({
      a <- optim(starts[[k]], objective, method = "L-BFGS-B", lower = lower, upper = upper,
                 control = list(maxit = maxit, factr = 1e7, pgtol = 1e-7))
      list(start = k, par = a$par, nll = a$value, convergence = a$convergence,
           message = if (is.null(a$message)) "" else a$message,
           evaluations = unname(a$counts[["function"]]))
    }, error = function(e) list(start = k, par = rep(NA_real_, length(lower)),
                                nll = Inf, convergence = 99L, message = conditionMessage(e),
                                evaluations = NA_integer_))
  })
  values <- vapply(attempts, function(a) a$nll, 0.0)
  # Keep the best likelihood even if its optimizer flag is nonzero, and expose
  # that flag. The caller must not silently treat it as a successful fit.
  best <- attempts[[which.min(values)]]
  if (!is.finite(best$nll) || best$nll >= 1e99) stop("Every optimizer start failed")
  fit <- gaussian_profile(best$par, blocks, q, ar, details = TRUE)
  names(fit$beta) <- colnames(X)
  dimnames(fit$vcov) <- list(colnames(X), colnames(X))
  fixed_fitted <- drop(X %*% fit$beta)
  conditional_fitted <- fixed_fitted
  # A converts centered/scaled random effects back to original predictor units.
  A <- if (q == 1L) matrix(1, 1L, 1L) else matrix(c(1, 0, -center / scale, 1 / scale), 2L, 2L)
  eb <- matrix(NA_real_, length(index), q, dimnames = list(names(index), if (q == 1L) "intercept" else c("intercept", "slope")))
  for (i in seq_along(index)) {
    j <- index[[i]]
    b <- blocks[[i]]
    u <- fit$H %*% crossprod(b$Z, chol_solve(fit$factors[[i]], y[j] - fixed_fitted[j]))
    conditional_fitted[j] <- fixed_fitted[j] + drop(b$Z %*% u)
    eb[i, ] <- drop(A %*% u)
  }
  evals <- eigen(fit$H, symmetric = TRUE, only.values = TRUE)$values
  fit$diagnostics <- list(convergence = best$convergence, message = best$message,
    selected_start = best$start, nll_start_range = diff(range(values[is.finite(values) & values < 1e99])),
    parameter_boundary = any(abs(best$par - lower) < 1e-4 | abs(best$par - upper) < 1e-4),
    ar_near_boundary = abs(fit$phi) > 0.99,
    random_near_singular = min(evals) < 1e-6 * max(1, max(evals)))
  fit$attempts <- attempts
  fit$theta <- best$par
  fit$random_covariance <- fit$sigma2 * A %*% fit$H %*% t(A)
  fit$random_effects <- eb
  fit$fixed_fitted <- fixed_fitted
  fit$conditional_fitted <- conditional_fitted
  fit$residual_marginal <- y - fixed_fitted
  fit$residual_conditional <- y - conditional_fitted
  fit$X <- X
  fit$Z <- Z
  fit$population <- group
  fit$year <- time
  fit$random <- random
  fit$ar <- ar
  fit$fixed <- deparse(fixed)
  fit$response <- response
  fit$random_x <- random_x
  fit$factors <- NULL
  fit
}
