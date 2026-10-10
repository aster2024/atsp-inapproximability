"""Exact rational bounds for the proved weighted-amplifier ATSP transfer."""

from fractions import Fraction


def main():
    matches_per_eq=15
    checker=Fraction(3,2)
    module=Fraction(17,2)
    baseline=matches_per_eq*checker+module
    assert baseline==31
    limit=(baseline+Fraction(1,2))/baseline
    assert limit==Fraction(63,62)>Fraction(73,72)
    eps=delta=lam=Fraction(1,100000)
    L=10**7
    yes=baseline+2*lam+(1+2*lam)*eps+(Fraction(5,2)+2*lam)*delta
    no=baseline+2*lam+Fraction(1,2)-eps-Fraction(36,L)
    ratio=no/yes
    assert ratio>Fraction(73,72)
    assert ratio>Fraction(64,63)  # clean explicit factor below 63/62
    assert Fraction(64,63)>Fraction(73,72)
    print({"result":"PASS","matching_per_equation":matches_per_eq,
           "baseline":str(baseline),"source_gap":"1/2","limit_ratio":str(limit),
           "explicit_target":"64/63","explicit_ratio":str(ratio),
           "yes_coefficient":str(yes),"no_coefficient":str(no),
           "parameters":{"epsilon":str(eps),"delta":str(delta),
                         "lambda":str(lam),"forced_path_length":L}})


if __name__=="__main__":
    main()
