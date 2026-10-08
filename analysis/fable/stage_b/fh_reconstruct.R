# Stage B (Fable's independent implementation): reconstruct the Fagan & Holmes
# (2006) terminal-trajectory statistics from the Williams et al. (2021) CC0 series.
#
# F&H Methods: multilevel mixed regression (Hedeker & Gibbons 1996 MIXREG):
# censuses nested in populations, random effects for populations, AR(1) errors
# within series, marginal maximum likelihood, non-zero censuses only. Extinct
# when N <= 1; time to extinction s (s = 0 at extinction); growth
# D_s = ln(N_s / N_{s+1}) with N_Final := 1 for the last transition.
# Published: T1 D ~ s: -0.50 + 0.034 s; T2 excluding final transition ("s >= 2"):
# -0.22 + 0.011 s; T3 squared residuals of T1 ~ s: 0.66 - 0.047 s;
# log scaling s = -15.9 + 9.1 ln N_s; period (s <= 9 vs >= 10) logarithmic fits
# -41.7 + 16.4 ln N (s >= 10) and -2.3 + 3.2 ln N (s <= 9), period z = 2.3.
#
# Ambiguities are exposed as variants, not resolved silently:
#   window  : "williams" (all Williams years up to the extinction census) or
#             "fh_length" (last L_FH years, L_FH from F&H Table 1, incl. extinction year)
#   re      : random intercept ("ri") or random intercept + slope ("ris")
#   excl    : final-transition exclusion as s >= 1 or s >= 2
# Run from repo root: Rscript analysis/fable/stage_b/fh_reconstruct.R

suppressMessages(library(nlme))

input <- "data/raw/williams2021/population_data.csv"
manifest <- read.csv("notes/t3/source_manifest.csv", stringsAsFactors = FALSE)
sha <- system2("sha256sum", input, stdout = TRUE)
stopifnot(sub(" .*", "", sha) == manifest$sha256[manifest$file == "population_data.csv"])

fh <- data.frame(
  pop = c("wild_dog", "marmot", "ms_woodpecker", "rc_woodpecker", "golden_plover",
          "whooping_crane", "hawaiian_crow", "wood_turtle_A", "wood_turtle_B"),
  wid = c(14, 15, 6, 20, 21, 10, 4, 8, 9),
  L_fh = c(20, 21, 16, 14, 18, 16, 12, 19, 19),
  stringsAsFactors = FALSE)

w <- read.csv(input, stringsAsFactors = FALSE, check.names = FALSE)
ycols <- grep("^[0-9]{4}$", names(w), value = TRUE)

series <- function(wid, window, L_fh) {
  v <- suppressWarnings(as.numeric(unlist(w[w$ID == wid, ycols])))
  yr <- as.integer(ycols)[!is.na(v)]; v <- v[!is.na(v)]
  ext <- which(v <= 1)[1]                      # F&H rule: extinct when N <= 1
  yr <- yr[seq_len(ext)]; v <- v[seq_len(ext)]
  if (window == "fh_length" && length(yr) > L_fh) {
    keep <- (length(yr) - L_fh + 1):length(yr); yr <- yr[keep]; v <- v[keep]
  }
  v[length(v)] <- 1                            # N_Final := 1
  data.frame(year = yr, N = v, s = max(yr) - yr)
}

build <- function(window) {
  do.call(rbind, lapply(seq_len(nrow(fh)), function(i) {
    d <- series(fh$wid[i], window, fh$L_fh[i]); d$pop <- fh$pop[i]
    d <- d[order(d$s), ]
    # transition into s from s+1: D_s = ln(N_s / N_{s+1}), defined for s = 0..max-1
    d$D <- c(log(d$N[-nrow(d)] / d$N[-1]), NA)
    d
  }))
}

fit_lme <- function(formula, data, re) {
  rnd <- if (re == "ri") ~ 1 | pop else as.formula(paste("~", all.vars(formula)[2], "| pop"))
  tryCatch(lme(formula, random = rnd, data = data, method = "ML",
               correlation = corAR1(form = ~ s | pop),
               control = lmeControl(opt = "optim", maxIter = 200, msMaxIter = 200)),
           error = function(e) NULL)
}

report <- function(window, re) {
  d <- build(window)
  g <- d[!is.na(d$D), ]
  cat(sprintf("\n=== window=%s  re=%s  populations=%d  non-zero censuses=%d  transitions=%d\n",
              window, re, length(unique(d$pop)), sum(d$s >= 1), nrow(g)))
  m1 <- fit_lme(D ~ s, g, re)
  if (is.null(m1)) { cat("T1 fit failed\n"); return(invisible()) }
  b <- fixef(m1); cat(sprintf("T1  D ~ s           : %+.3f %+.4f s   (published -0.50 +0.034)\n", b[1], b[2]))
  for (smin in 1:2) {
    m <- fit_lme(D ~ s, g[g$s >= smin, ], re)
    if (!is.null(m)) { b <- fixef(m)
      cat(sprintf("T2  D ~ s, s>=%d     : %+.3f %+.4f s   (published -0.22 +0.011)\n", smin, b[1], b[2])) }
  }
  g$r2m <- residuals(m1, level = 0)^2; g$r2c <- residuals(m1, level = 1)^2
  for (lv in c("r2m", "r2c")) {
    m <- fit_lme(as.formula(paste(lv, "~ s")), g, re)
    if (!is.null(m)) { b <- fixef(m)
      cat(sprintf("T3  %s ~ s          : %+.3f %+.4f s   (published 0.66 -0.047)\n", lv, b[1], b[2])) }
  }
  n <- d[d$s >= 1, ]; n$lnN <- log(n$N)
  m <- fit_lme(s ~ lnN, n, re)
  if (!is.null(m)) { b <- fixef(m); cat(sprintf("Scale s ~ ln N      : %+.2f %+.2f lnN   (published -15.9 +9.1)\n", b[1], b[2])) }
  n$late <- factor(ifelse(n$s <= 9, "le9", "ge10"), levels = c("ge10", "le9"))
  m <- fit_lme(s ~ lnN * late, n, re)
  if (!is.null(m)) {
    tt <- summary(m)$tTable
    cat(sprintf("T5  s ~ lnN*period  : ge10 %+.1f %+.1f lnN; le9 %+.1f %+.1f lnN; t(period)=%.2f t(interaction)=%.2f\n",
                tt[1, 1], tt[2, 1], tt[1, 1] + tt[3, 1], tt[2, 1] + tt[4, 1], tt[3, 4], tt[4, 4]))
    cat("    (published ge10: -41.7 +16.4 ln N; le9: -2.3 +3.2 ln N; z(period) = 2.3)\n")
  }
}

for (window in c("williams", "fh_length")) for (re in c("ri", "ris")) report(window, re)
