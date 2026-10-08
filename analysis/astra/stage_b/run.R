# Run from the repository root: Rscript analysis/astra/stage_b/run.R OUTPUT_DIR
source("analysis/astra/stage_b/gaussian_ml.R")
source("analysis/astra/stage_b/data.R")
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L || dir.exists(args[1L])) stop("Supply one new output directory")
out <- args[1L]
dir.create(out, recursive = TRUE)
d <- load_fh_data()
write.csv(d$metadata, file.path(out, "input_windows.csv"), row.names = FALSE)
write.csv(d$growth, file.path(out, "growth_input.csv"), row.names = FALSE)
write.csv(d$scaling, file.path(out, "scaling_input.csv"), row.names = FALSE)
fits <- list()
failures <- list()
fit_once <- function(label, data, response, fixed, random_x, random, ar) {
  cat(format(Sys.time(), "%FT%T%z"), label, "\n")
  started <- proc.time()[["elapsed"]]
  result <- tryCatch(fit_gaussian_ml(data, response, fixed, random_x, random, ar), error = identity)
  if (inherits(result, "error")) {
    failures[[label]] <<- conditionMessage(result)
    cat("FAILED:", conditionMessage(result), "\n")
    return(NULL)
  }
  result$elapsed_seconds <- proc.time()[["elapsed"]] - started
  fits[[label]] <<- result
  cat("n =", result$n, "; logLik =", -result$nll, "; phi =", result$phi,
      "; convergence =", result$diagnostics$convergence, "\n")
  if (result$diagnostics$convergence != 0L) {
    failures[[label]] <<- paste("Nonconverged selected fit; dependent statistics skipped:", result$diagnostics$message)
    cat("INVALID FOR DOWNSTREAM USE:", failures[[label]], "\n")
    return(NULL)
  }
  result
}
variants <- list(RIRS_AR1 = list("intercept_slope", TRUE),
                 RI_AR1 = list("intercept", TRUE),
                 RIRS_IID = list("intercept_slope", FALSE))
for (v in names(variants)) {
  random <- variants[[v]][[1L]]
  ar <- variants[[v]][[2L]]
  mean_fits <- list()
  for (cutoff in 0:2) {
    dd <- subset(d$growth, s >= cutoff)
    label <- paste(v, paste0("growth_sge", cutoff), sep = "/")
    m <- fit_once(label, dd, "growth", ~s, "s", random, ar)
    mean_fits[[as.character(cutoff)]] <- m
    if (is.null(m)) next
    for (resid_type in c("conditional", "marginal")) {
      dd$squared_residual <- m[[paste0("residual_", resid_type)]]^2
      fit_once(paste(v, paste0("variance_refit_sge", cutoff), resid_type, sep = "/"),
               dd, "squared_residual", ~s, "s", random, ar)
    }
  }
  full_mean <- mean_fits[["0"]]
  if (!is.null(full_mean)) {
    for (resid_type in c("conditional", "marginal")) {
      dd <- d$growth
      dd$squared_residual <- full_mean[[paste0("residual_", resid_type)]]^2
      for (cutoff in 1:2) {
        fit_once(paste(v, paste0("variance_subset_sge", cutoff), resid_type, sep = "/"),
                 subset(dd, s >= cutoff), "squared_residual", ~s, "s", random, ar)
      }
    }
  }
  fit_once(paste0(v, "/scaling"), d$scaling, "s", ~log_count, "log_count", random, ar)
  fit_once(paste0(v, "/period_additive"), d$scaling, "s", ~log_count + late, "log_count", random, ar)
  fit_once(paste0(v, "/period_interaction"), d$scaling, "s", ~log_count * late, "log_count", random, ar)
  for (period in 0:1) {
    fit_once(paste0(v, "/period_separate_", if (period == 0) "early" else "late"),
             subset(d$scaling, late == period), "s", ~log_count, "log_count", random, ar)
  }
}
coef_table <- do.call(rbind, lapply(names(fits), function(label) {
  f <- fits[[label]]
  se <- sqrt(diag(f$vcov))
  data.frame(model = label, term = names(f$beta), estimate = unname(f$beta), se = se,
    conditional_wald_z = unname(f$beta) / se, n = f$n, log_likelihood = -f$nll,
    phi = f$phi, sigma = sqrt(f$sigma2), convergence = f$diagnostics$convergence,
    parameter_boundary = f$diagnostics$parameter_boundary, ar_near_boundary = f$diagnostics$ar_near_boundary,
    random_near_singular = f$diagnostics$random_near_singular,
    nll_start_range = f$diagnostics$nll_start_range, elapsed_seconds = f$elapsed_seconds,
    row.names = NULL)
}))
write.csv(coef_table, file.path(out, "coefficients.csv"), row.names = FALSE)
attempt_table <- do.call(rbind, lapply(names(fits), function(label) do.call(rbind, lapply(fits[[label]]$attempts, function(a) {
  data.frame(model = label, start = a$start, nll = a$nll, convergence = a$convergence,
    evaluations = a$evaluations, message = a$message, parameters = paste(signif(a$par, 12), collapse = ";"))
}))))
write.csv(attempt_table, file.path(out, "optimizer_attempts.csv"), row.names = FALSE)
eb_table <- do.call(rbind, lapply(names(fits)[grepl("/scaling$", names(fits))], function(label) {
  f <- fits[[label]]
  data.frame(model = label, population = rownames(f$random_effects),
    intercept = f$beta[["(Intercept)"]] + f$random_effects[, "intercept"],
    slope = f$beta[["log_count"]] + if (ncol(f$random_effects) == 2L) f$random_effects[, "slope"] else 0)
}))
write.csv(eb_table, file.path(out, "scaling_empirical_bayes.csv"), row.names = FALSE)
writeLines(if (length(failures)) paste(names(failures), unlist(failures), sep = ": ") else "None", file.path(out, "failures.txt"))
saveRDS(list(fits = fits, failures = failures, input_sha256 = d$input_sha256), file.path(out, "fits.rds"))
capture.output(sessionInfo(), file = file.path(out, "sessionInfo.txt"))
cat("Archived", length(fits), "fits;", length(failures), "failed or nonconverged models.\n")
