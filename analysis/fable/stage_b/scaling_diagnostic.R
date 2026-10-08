# Diagnostic for the F&H time-to-extinction scaling model (s ~ ln N), which fh_reconstruct.R
# does not reproduce: compares AR(1)/no-AR(1) and random-effect variants with OLS fits.
# Reuses build()/series() from fh_reconstruct.R. Run from repo root.
source_lines <- readLines("analysis/fable/stage_b/fh_reconstruct.R")
eval(parse(text = source_lines[1:grep("^report <- function", source_lines) - 1]))
d <- build("williams"); n <- d[d$s >= 1, ]; n$lnN <- log(n$N)
show <- function(lab, m) { if (is.null(m)) { cat(lab, ": failed\n"); return() }
  phi <- tryCatch(coef(m$modelStruct$corStruct, unconstrained = FALSE), error = function(e) NA); if (length(phi) == 0) phi <- NA
  cat(sprintf("%-28s int %+7.2f slope %+6.2f  phi %s  logLik %.1f\n", lab, fixef(m)[1], fixef(m)[2],
              ifelse(is.na(phi[1]), "-", sprintf("%.3f", phi[1])), logLik(m))) }
ctl <- lmeControl(opt = "optim", maxIter = 500, msMaxIter = 500)
show("RI, AR1", tryCatch(lme(s ~ lnN, random = ~1|pop, n, method="ML", correlation=corAR1(form=~s|pop), control=ctl), error=function(e) NULL))
show("RI+RS, AR1", tryCatch(lme(s ~ lnN, random = ~lnN|pop, n, method="ML", correlation=corAR1(form=~s|pop), control=ctl), error=function(e) NULL))
show("RI, no AR", tryCatch(lme(s ~ lnN, random = ~1|pop, n, method="ML", control=ctl), error=function(e) NULL))
show("RI+RS, no AR", tryCatch(lme(s ~ lnN, random = ~lnN|pop, n, method="ML", control=ctl), error=function(e) NULL))
cat("OLS pooled:", round(coef(lm(s ~ lnN, n)), 2), "\n")
cat("per-population OLS slopes:\n"); print(round(sapply(split(n, n$pop), function(x) coef(lm(s ~ lnN, x))[2]), 2))
cat("F&H Table 1 slopes: dog 9.17 marmot 9.26 msw 9.26 rcw 8.47 plover 7.04 crane 9.26 crow 9.17 turtleA 8.55 turtleB 8.13\n")
# period model without AR
n$late <- factor(ifelse(n$s <= 9, "le9", "ge10"), levels = c("ge10", "le9"))
m <- tryCatch(lme(s ~ lnN * late, random = ~lnN|pop, n, method="ML", control=ctl), error=function(e) NULL)
if (!is.null(m)) { tt <- summary(m)$tTable; print(round(tt, 3)) }
