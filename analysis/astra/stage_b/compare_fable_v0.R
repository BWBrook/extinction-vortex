# Post-freeze comparison. Run after checking out the Fable and Astra snapshots.
# Rscript analysis/astra/stage_b/compare_fable_v0.R NEW_OUTPUT_DIR
source("analysis/astra/stage_b/gaussian_ml.R")
source("analysis/astra/stage_b/data.R")
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L || dir.exists(args[1L])) stop("Supply one new output directory")
dir.create(args[1L], recursive = TRUE)
out <- args[1L]
peer <- new.env(parent = globalenv())
expressions <- parse("analysis/fable/stage_b/fh_reconstruct.R")
for (expression in expressions) {
  if (is.call(expression) && identical(expression[[1L]], as.name("<-")) &&
      identical(expression[[2L]], as.name("report"))) break
  eval(expression, envir = peer)
}
a <- load_fh_data()
b <- peer$build("williams")
b$population <- sprintf("FH%02d", match(b$pop, peer$fh$pop))
g <- b[!is.na(b$D), ]
n <- b[b$s >= 1, ]
n$lnN <- log(n$N)
n$late <- factor(ifelse(n$s <= 9, "le9", "ge10"), levels = c("ge10", "le9"))
idx <- match(paste(a$growth$population, a$growth$year), paste(g$population, g$year))
jdx <- match(paste(a$scaling$population, a$scaling$year), paste(n$population, n$year))
stopifnot(nrow(g) == nrow(a$growth), nrow(n) == nrow(a$scaling),
          !anyNA(idx), !anyNA(jdx), max(abs(a$growth$growth - g$D[idx])) < 1e-12,
          identical(a$growth$s, g$s[idx]), identical(a$scaling$s, n$s[jdx]),
          max(abs(a$scaling$log_count - n$lnN[jdx])) < 1e-12)
writeLines("Growth and scaling inputs match for all 149 observations after ordering by population and year.", file.path(out, "input_comparison.txt"))
frozen <- readRDS("analysis/astra/stage_b/results_v0/reconstruction/fits.rds")$fits
rows <- list()
matched_likelihood <- function(m) {
  dd <- nlme::getData(m)
  mf <- model.frame(formula(m), dd)
  X <- model.matrix(formula(m), dd)
  y <- model.response(mf)
  x <- dd[[all.vars(formula(m))[2L]]]
  G <- as.matrix(nlme::getVarCov(m, type = "random.effects")) / m$sigma^2
  q <- nrow(G)
  A <- if (q == 1L) matrix(1, 1L, 1L) else matrix(c(1, 0, -mean(x) / sd(x), 1 / sd(x)), 2L, 2L)
  H <- solve(A) %*% G %*% t(solve(A))
  L <- t(chol(H))
  theta <- if (q == 1L) log(L[1L, 1L]) else c(log(L[1L, 1L]), L[2L, 1L], log(L[2L, 2L]))
  phi <- as.numeric(coef(m$modelStruct$corStruct, unconstrained = FALSE))
  theta <- c(theta, atanh(phi))
  Z <- if (q == 1L) matrix(1, length(y), 1L) else cbind(1, (x - mean(x)) / sd(x))
  blocks <- lapply(split(seq_along(y), dd$pop), function(j) list(y = y[j], X = X[j, , drop = FALSE],
    Z = Z[j, , drop = FALSE], time = dd$year[j]))
  check <- gaussian_profile(theta, blocks, q, TRUE, details = TRUE)
  c(log_likelihood_difference = -check$nll - as.numeric(logLik(m)),
    max_fixed_effect_difference = max(abs(check$beta - nlme::fixef(m))))
}
record <- function(label, m) {
  if (is.null(m)) stop(paste("Peer comparison fit failed:", label))
  check <- matched_likelihood(m)
  beta <- nlme::fixef(m)
  names(beta) <- sub("latele9", "late", sub("lnN", "log_count", names(beta), fixed = TRUE), fixed = TRUE)
  aa <- frozen[[label]]
  rows[[label]] <<- data.frame(model = label, term = names(beta), peer_estimate = unname(beta),
    astra_v0_estimate = unname(aa$beta[names(beta)]), coefficient_difference = unname(aa$beta[names(beta)] - beta),
    peer_log_likelihood = as.numeric(logLik(m)), astra_v0_log_likelihood = -aa$nll,
    matched_covariance_log_likelihood_difference = check[1L],
    matched_covariance_max_coefficient_difference = check[2L], row.names = NULL)
}
for (re in c("ri", "ris")) {
  prefix <- if (re == "ri") "RI_AR1/" else "RIRS_AR1/"
  m1 <- peer$fit_lme(D ~ s, g, re)
  record(paste0(prefix, "growth_sge0"), m1)
  for (cutoff in 1:2) record(paste0(prefix, "growth_sge", cutoff), peer$fit_lme(D ~ s, g[g$s >= cutoff, ], re))
  for (kind in c("marginal", "conditional")) {
    gg <- g
    gg$r2 <- residuals(m1, level = if (kind == "marginal") 0 else 1, type = "response")^2
    record(paste0(prefix, "variance_refit_sge0/", kind), peer$fit_lme(r2 ~ s, gg, re))
  }
  record(paste0(prefix, "scaling"), peer$fit_lme(s ~ lnN, n, re))
  record(paste0(prefix, "period_interaction"), peer$fit_lme(s ~ lnN * late, n, re))
}
result <- do.call(rbind, rows)
write.csv(result, file.path(out, "comparison.csv"), row.names = FALSE)
capture.output(sessionInfo(), file = file.path(out, "sessionInfo.txt"))
stopifnot(max(abs(result$matched_covariance_log_likelihood_difference)) < 1e-5,
          max(abs(result$matched_covariance_max_coefficient_difference)) < 1e-5)
cat("Compared 14 fitted models and their likelihoods at matching covariance parameters.\n")
cat("Max matched logLik difference:", max(abs(result$matched_covariance_log_likelihood_difference)), "\n")
cat("Max matched coefficient difference:", max(abs(result$matched_covariance_max_coefficient_difference)), "\n")
cat("Separately optimized coefficient differences are retained, not treated as equality.\n")
