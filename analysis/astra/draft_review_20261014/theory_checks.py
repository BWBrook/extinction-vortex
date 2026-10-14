"""Exact finite examples for draft review; no population simulation or fitting."""
from fractions import Fraction as F
import json
from pathlib import Path


def normalise(weights):
    total = sum(weights)
    return [w/total for w in weights]


def ess(weights):
    return sum(weights)**2/sum(w*w for w in weights)


def main():
    prior = [F(1,2), F(1,2)]
    selection = [F(1,10), F(9,10)]
    evidence = [F(9,10), F(1,10)]
    joint_then_selected = normalise([p*q*l for p,q,l in zip(prior,selection,evidence)])
    fixed_theta_then_selected = normalise([p*l for p,l in zip(prior,evidence)])
    assert joint_then_selected == [F(1,2),F(1,2)]
    assert fixed_theta_then_selected == [F(9,10),F(1,10)]
    corrected = normalise([p*q*l/q for p,q,l in zip(prior,selection,evidence)])
    assert corrected == fixed_theta_then_selected

    # One shared annual survival probability, P=0.2 or 0.8 equiprobably.
    n = 10
    mean_p,var_p = F(1,2), F(9,100)
    independent_binomial_variance = n*mean_p*(1-mean_p)
    shared_year_variance = independent_binomial_variance+n*(n-1)*var_p
    assert shared_year_variance == F(53,5) and independent_binomial_variance == F(5,2)
    # One shared annual per-capita recruitment rate, F=0.2 or 1.8 equiprobably.
    mean_f,var_f = F(1),F(16,25)
    poisson_variance = n*mean_f
    mixed_poisson_variance = poisson_variance+n*n*var_f
    assert mixed_poisson_variance == 74 and poisson_variance == 10
    # Outcomes conditionally independent given the same two-point environment.
    cov_p_f = (F(1,5)*F(1,5)+F(4,5)*F(9,5))/2-mean_p*mean_f
    assert n*n*cov_p_f == 24

    before,after = ess([F(1)]*10),ess([F(1)]*10+[F(100)])
    assert before == 10 and after < before
    failure = {str(float(q)):float(1-(1-q)**9) for q in [F(1,100),F(1,10)]}
    assert failure['0.01'] > .08

    result = {
        'scope':'Exact illustrative probability/variance arithmetic, not project simulation or empirical analysis.',
        'selection':{
            'prior':[float(x) for x in prior],
            'P_selection_given_theta':[float(x) for x in selection],
            'P_evidence_given_theta':[float(x) for x in evidence],
            'theta_posterior_joint_then_selection':[float(x) for x in joint_then_selected],
            'theta_posterior_fixed_theta_then_conditioned_path':[float(x) for x in fixed_theta_then_selected],
            'inverse_selection_weight_restores_second_target':corrected==fixed_theta_then_selected},
        'shared_year':{
            'n':n,'survival_mean':float(n*mean_p),
            'binomial_variance':float(independent_binomial_variance),
            'shared_environment_survival_variance':float(shared_year_variance),
            'recruitment_mean':float(n*mean_f),
            'poisson_variance':float(poisson_variance),
            'shared_environment_recruitment_variance':float(mixed_poisson_variance),
            'survival_recruitment_covariance':float(n*n*cov_p_f)},
        'ESS_nonmonotone':{'ten_unit_weights':float(before),'after_adding_weight_100':float(after)},
        'any_of_nine_failure_under_independent_pair_failures':failure,
        'limitations':[
            'Two-point examples demonstrate logical differences; they are not estimated project effect sizes.',
            'Any-of-nine formula assumes independent population failures solely for illustration.',
            'No data downloaded, random values generated, model fitted or bank loaded.']}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
