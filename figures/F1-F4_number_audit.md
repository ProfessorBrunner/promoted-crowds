
### F1 (12 elements)

| element | plotted value (full precision) | archive source | kind | promoted_crowds.tex |
|---|---|---|---|---|
| exact time-dependent ratio curve | 1.2702500791 … 1.9698145484  (n=601) | F1_exact_curves.csv:ratio_time_dependent_exact | computed | L462 table, tau0=10 row: 1.9698145 |
| exact frozen-proxy curve | 1.0 … 1.969802279  (n=601) | F1_exact_curves.csv:ratio_frozen_proxy_exact | computed | L477 'increases with 1-e^{-rho tau0} and approaches 1.969846' |
| time-dependent markers (6) | 1.274793164492937 … 1.9628228682589426  (n=6) | F1_measured.csv:ratio_timedep_measured | computed | L462 tau0=10 row: 1.96282 +- 0.00624 |
| frozen-proxy markers (6) | 1.000438009636212 … 1.964772638663124  (n=6) | F1_measured.csv:ratio_frozen_measured | computed | not tabulated in tex |
| error bars = t x sem (time-dep) | 0.010993595406064071 … 0.01290352961388236  (n=6) | F1_measured.csv:ratio_timedep_sem x t_multiplier_df23 | computed | L504 caption 'error bars are t_{0.975,23}=2.069 times the standard error' |
| error bars = t x sem (frozen) | 0.008402243649401854 … 0.012571777669943053  (n=6) | F1_measured.csv:ratio_frozen_sem x t_multiplier_df23 | computed | L504 as above |
| '$t_{0.975,23}=2.069$' in parameter block | 2.0686576104190486 | F1_measured.csv:t_multiplier_df23 | computed | L504 caption: 2.069 |
| dotted reference line labelled '$1+x_2=1.9698$' | 1.969846310392954 | F1_measured.csv:stationary_ratio_1_plus_x2 <- stage2/outputs_v1/sealed_predictions.json P1_registered_reproduction (40,140,50).x (= ratio of the two R_over_lambda to 2.2e-16) | computed | L504 caption 'stationary ratio 1+x_2=1.9698'; L468/L477 stationary 1.969846 |
| dotted reference line at unity | 1.0 | literal in make_figures.py | transcribed | L477 'the proxy is exactly 1' at tau0=0 |
| annotation 'proxy ratio exactly 1' | 1 (exact, at tau0=0) | F1_exact_curves.csv:ratio_frozen_proxy_exact[0]=1.0 | computed | L477 'the proxy is exactly 1' |
| parameter block 'rho=eps=1, lambda=2, N=10^5, L=ln 2' | rho=1, eps=1, lambda=2, N=100000, L=ln2 | design parameters (Sec. IV-C-1) | transcribed | L504 'at lambda=2 and N=10^5' |
| parameter block '24 backgrounds x 10^4 seed trials' | 24, 10000 | design: stage2 P1-delay replicate structure | transcribed | L504 '24 backgrounds of 10^4 seed trials each' |

### F2 (39 elements)

| element | plotted value (full precision) | archive source | kind | promoted_crowds.tex |
|---|---|---|---|---|
| (a) point (40, 50, 140) at lambda=1.0 | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 50, 140) at lambda=1.0 | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (40, 140, 50) at lambda=1.0 | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 140, 50) at lambda=1.0 | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (40, 50, 140) at lambda=2.0 | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 50, 140) at lambda=2.0 | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (40, 140, 50) at lambda=2.0 | 0.4592901878914405 | F2_outbreak_probability.csv p_outbreak (440/958) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 140, 50) at lambda=2.0 | [0.4279587758231989, 0.4909467784293334] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (40, 50, 140) at lambda=3.5 | 0.3429423459244533 | F2_outbreak_probability.csv p_outbreak (345/1006) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 50, 140) at lambda=3.5 | [0.3142562148542051, 0.3728233784425201] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (40, 140, 50) at lambda=3.5 | 0.873015873015873 | F2_outbreak_probability.csv p_outbreak (275/315) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (40, 140, 50) at lambda=3.5 | [0.8316998640741977, 0.9053435582874978] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (50, 40, 140) (held out) at lambda=2.0 | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (50, 40, 140) (held out) at lambda=2.0 | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) point (140, 40, 50) (held out) at lambda=2.0 | 0.4790874524714829 | F2_outbreak_probability.csv p_outbreak (504/1052) | computed | L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed |
| (a) Wilson interval (140, 40, 50) (held out) at lambda=2.0 | [0.4490307079838821, 0.5092963688396165] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'A 0/50 observation has interval [0,0.0713]' |
| (a) star marker, N=10^6, lambda=2 | 0.36 (= 18/50) | F2_outbreak_probability.csv prediction='P1 (N=1e6)' | computed | L517 'the star marks 18/50 at N=10^6, lambda=2' |
| (a) star Wilson interval | [0.24138749651846741, 0.49858983123887307] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | not quoted in tex |
| (a) annotation '0/50 at both orders at lambda=1' | 0/50, 0/50 | F2_outbreak_probability.csv outbreaks/replicates at lam=1.0 | computed | L1477 'Such cells occur at lambda=1 for both stance orders' |
| (a) Wilson note '[0, 0.0713]' | 0.07134759913335872 | F2_outbreak_probability.csv:ci_hi (0/50 cell) | computed | L517 and L1477: [0,0.0713] |
| (a) Wilson note 'half-width 0.0357' | 0.035673799566679355 | F2_outbreak_probability.csv:half_width | computed | L1477 half-width 0.0357 |
| (a) Wilson note 'precision targets 0.03 and 0.02' | 0.03, 0.02 | design A4a; literals in make_figures.py | transcribed | L1475 'stance experiments use target 0.03 ... orientation experiments use target 0.02' |
| (a) lambda values plotted | 1.0, 2.0, 3.5 | F2_outbreak_probability.csv:lam | computed | L517 'lambda in {1,2,3.5}' |
| (a) panel label 'N=10^5 unless marked' | 100000 | F2_outbreak_probability.csv:N | computed | L517 '(a) ... at N=10^5' |
| (b) point (10, 20, 30) | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L512/L517 '0/50, 75/1157=0.065, and 0/50' |
| (b) printed 'R=0.962' | 0.9616068133888933 | lam x F2_outbreak_probability.csv:q_T x ln(1/0.95); q_T <- stage2/outputs_v1/stage2_results.json sealed.P2_reproduction[order].q_T | computed (replaced transcribed R_registered in this pass) | L512/L517 'R=0.962, 1.032, and 0.867' |
| (b) printed count (10, 20, 30) | 0/50 | F2_outbreak_probability.csv:outbreaks/replicates | computed | L512 '0/50, 75/1157=0.065, and 0/50' |
| (b) Wilson interval (10, 20, 30) | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'nominal 95% Wilson intervals' |
| (b) point (10, 30, 20) | 0.06482281763180639 | F2_outbreak_probability.csv p_outbreak (75/1157) | computed | L512/L517 '0/50, 75/1157=0.065, and 0/50' |
| (b) printed 'R=1.032' | 1.0318091348389808 | lam x F2_outbreak_probability.csv:q_T x ln(1/0.95); q_T <- stage2/outputs_v1/stage2_results.json sealed.P2_reproduction[order].q_T | computed (replaced transcribed R_registered in this pass) | L512/L517 'R=0.962, 1.032, and 0.867' |
| (b) printed count (10, 30, 20) | 75/1157 | F2_outbreak_probability.csv:outbreaks/replicates | computed | L512 '0/50, 75/1157=0.065, and 0/50' |
| (b) Wilson interval (10, 30, 20) | [0.05202632040652725, 0.0804994932192047] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'nominal 95% Wilson intervals' |
| (b) point (20, 10, 30) | 0.0 | F2_outbreak_probability.csv p_outbreak (0/50) | computed | L512/L517 '0/50, 75/1157=0.065, and 0/50' |
| (b) printed 'R=0.867' | 0.8670234815632141 | lam x F2_outbreak_probability.csv:q_T x ln(1/0.95); q_T <- stage2/outputs_v1/stage2_results.json sealed.P2_reproduction[order].q_T | computed (replaced transcribed R_registered in this pass) | L512/L517 'R=0.962, 1.032, and 0.867' |
| (b) printed count (20, 10, 30) | 0/50 | F2_outbreak_probability.csv:outbreaks/replicates | computed | L512 '0/50, 75/1157=0.065, and 0/50' |
| (b) Wilson interval (20, 10, 30) | [6.938893903907228e-18, 0.07134759913335872] | F2_outbreak_probability.csv ci_lo/ci_hi | computed | L517 'nominal 95% Wilson intervals' |
| (b) panel label 'lambda=26.5, N=10^5' | 26.5, 100000 | F2_outbreak_probability.csv lam/N | computed | L517 '(b) Orientation-memory campaigns at lambda=26.5 ... panel (b) has N=10^5' |
| footnote 'pilot of 50 ... cap 1200' | 50, 1200 | design A4a adaptive rule; literals in make_figures.py | transcribed | L1475 'begin with 50 pilot replicates ... min[max(need,50),1200]' |
| footnote 'fixed 50-run design' for the N=10^6 cells | 50 | F2_outbreak_probability.csv:replicates | computed | L517 'the star marks 18/50 at N=10^6' |

### F3 (16 elements)

| element | plotted value (full precision) | archive source | kind | promoted_crowds.tex |
|---|---|---|---|---|
| agent mean curve | 1.0 … 0.0  (n=1401) | F3_P6A_agent.csv:mean_A | computed | L623 'agent mean is shown' |
| agent band (2.5th/97.5th pct) | lo 1.0 … 0.0  (n=1401) | F3_P6A_agent.csv:pct2p5_A/pct97p5_A | computed | L623 'pointwise 2.5th-97.5th percentiles across replicate trajectories' |
| kinetic curve | 1.0 … 0.0  (n=38006) | F3_P6A_kinetic.csv:A_kinetic | computed | L623 'kinetic curve is evaluated at the finest step h=0.0025' |
| reference line / label '$A_f=0.5603$' | 0.5603 | F3_marks.json:crossing_level <- stage2/config/stage2_config.py:163 | transcribed (declared crossing marker; no computed counterpart in archives) | L623 'fold activity A_f=0.5603'; L1447 'The marker is A_f=0.5603'; L612 Prop. 4 fold activity A_f=0.5603318, which CS reproduces as 0.5603318621202521 +-4.5e-09 (caseA_fold_v2.json) and the D.3 measure solver as 0.5603420775436564 +-4.22e-05 (caseA_fold_measure_solver.json) -- AGREES; the figure marks the declared level, a distinct quantity |
| vertical line / label 'adiabatic $t_{ad,f}=66.309$' | 66.30914996690508 | F3_marks.json:adiabatic <- stage2b/outputs/raw/caseA_fold_v2.json construction 'mixture_n1' (C.7.2 dose mixture, n = 1+Poisson(H)); t_ad,f = int_0^{H_f} du/(lambda A_+(u)) | computed (+-7.2e-09 on the ladder; confirmed by the D.3 measure solver at 66.30902252788111 +-7.29e-04 in caseA_fold_measure_solver.json; reproduces the manuscript to 3.3e-08. Was a transcribed constant until BUGLOG S2B-CS1 was fixed) | L623 't_{ad,f}=66.309'; L612/L618/L1532 '66.30915' -- AGREES |
| marked crossing point (t, A) | (70.35303633651682, 0.5603) | F3_marks.json:agent_t_dagger_mean, crossing_level | computed | L623 'mean replicate crossing time is 70.3530' |
| annotation 'agent mean 70.3530' | 70.35303633651682 | F3_marks.json:agent_t_dagger_mean | computed | L623/L1528: 70.3530 |
| annotation '95% CI [70.3288, 70.3773]' | [70.32878516161954, 70.37728751141411] | F3_marks.json:agent_t_dagger_mean_CI_lo/hi | computed | L623/L1528: [70.3288,70.3773] |
| annotation 'half-width 0.0243' | 0.02425117489728846 | F3_marks.json:agent_t_dagger_mean_95_halfwidth | computed | L618/L1530 'Monte Carlo 95% half-width 0.024' |
| annotation 'kinetic reference 70.3277 +- 0.0244' | 70.32768783769728 +- 0.024354959755214622 | F3_marks.json:kinetic_t_dagger_reference(_unc) <- stage2b/outputs/raw/p6_reference.json case_A_kinetic.t_dagger.richardson/uncertainty | computed | L623 '70.3277+-0.0244'; L1447 'Extrapolation gives 70.327688, with error estimate 0.024355' |
| annotation 'Richardson, h=0.0100052/0.0050026/0.0024997' | [0.010005173926926205, 0.0050025869634631025, 0.0024996952111361955] | F3_marks.json:kinetic_h_ladder <- stage2b/outputs/raw/p6_reference.json case_A_kinetic.rows[*].h | computed (replaced transcribed 0.01/0.005/0.0025 in this pass) | L1447 'At h=(0.0100052,0.0050026,0.0024997)' |
| annotation 'p=1.059' | 1.0586374161315752 | F3_marks.json:kinetic_observed_order_in_h <- p6_reference.json observed_order | computed | L1447 'with order 1.059' |
| annotation 'kinetic finest grid 70.3033' | 70.30333287794207 | F3_marks.json:kinetic_t_dagger_finest_grid <- p6_reference.json value_finest | computed | L1447 'The finest-step value is 70.3033' |
| legend 'kinetic, finest grid h=0.0025' | 0.0024996952111361955 | F3_marks.json:kinetic_h <- p6_reference.json rows[2].h | computed | L623 'finest step h=0.0025'; L1447 'the plotted curve uses h=0.0025' |
| legend 'N=10^5, 50 replicates' | 100000, 50 | F3_marks.json:N, replicates | computed | L623 'Case A activity A(t) at N=10^5 ... 50 replicate trajectories' |
| annotation '49 df' | 49 (= replicates-1 = 49) | literal in make_figures.py; equals F3_marks.json replicates-1 | transcribed (identical to computed value) | L623/L1528 '49 degrees of freedom' |

### F4 (20 elements)

| element | plotted value (full precision) | archive source | kind | promoted_crowds.tex |
|---|---|---|---|---|
| (a) kinetic f_c^MF at lambda=1.6 | 0.13268101289127351 +- 0.0009343111371823976 | F4a_class2_onset.csv:f_c_MF/f_c_MF_unc | computed | tab:threshold L708-710 kinetic threshold f_c |
| (a) agent f_50 at lambda=1.6 | 0.13342201463414632 [0.13258753639689577, 0.13421982] | F4a_class2_onset.csv:f50_agent/f50_lo/f50_hi | computed | tab:threshold L708-710 finite-population 50% point and 95% interval |
| (a) kinetic f_c^MF at lambda=1.75 | 0.04406947071190815 +- 0.0004839526886878248 | F4a_class2_onset.csv:f_c_MF/f_c_MF_unc | computed | tab:threshold L708-710 kinetic threshold f_c |
| (a) agent f_50 at lambda=1.75 | 0.04381454117647059 [0.04336091764705882, 0.044434493333333325] | F4a_class2_onset.csv:f50_agent/f50_lo/f50_hi | computed | tab:threshold L708-710 finite-population 50% point and 95% interval |
| (a) kinetic f_c^MF at lambda=1.9 | 0.007082102536306744 +- 0.00026050088909657966 | F4a_class2_onset.csv:f_c_MF/f_c_MF_unc | computed | tab:threshold L708-710 kinetic threshold f_c |
| (a) agent f_50 at lambda=1.9 | 0.00731044 [0.006475964102564102, 0.007632992307692307] | F4a_class2_onset.csv:f50_agent/f50_lo/f50_hi | computed | tab:threshold L708-710 finite-population 50% point and 95% interval |
| (a) vertical line / label 'lambda_fold=1.482508' | 1.4825083314571268 | F4_marks.csv:lambda_fold <- stage2b/fold_exact.py (stage2b/outputs/raw/fold_exact.json) | computed | L722/L1457/L1584: 1.482508 |
| (a) vertical line / label 'lambda_c=1.95762' | 1.9576151889712174 | F4_marks.csv:lambda_c <- stage2/outputs_v1/stage2_results.json lambda_c_computed | computed (replaced transcribed 1.957615 in this pass) | L722/L669/L1457: 1.9576 (= 1/ln(5/3)) |
| (a) shaded 'bistable window' span | [1.4825083314571268, 1.9576151889712174] | F4_marks.csv:lambda_fold, lambda_c | computed | L722 'with lambda_fold=1.482508 and lambda_c=1.9576 marked' |
| (a) panel label 'alpha=0.5, c_b=0.3, eps=1, r=1' | 0.5, 0.3, 1, 1 | design parameters (Theorem 3 example) | transcribed | L722 'alpha=0.5, c_b=0.3, r=1' |
| (a) legend 'agent f_50 (N=5x10^4)' | 50000 | design parameter | transcribed | L722 'the finite-population points use N=5x10^4' |
| (b) trace lam1.0_f0.01 mean and band | mean 0.010085 … 0.0  (n=7001) | F4b_P5_traces.csv:lam1.0_f0.01_mean/_lo/_hi | computed | L722 '(b) active fraction A(t) at lambda=1,2 for f=0.01,0.10' |
| (b) trace lam1.0_f0.1 mean and band | mean 0.0998286 … 0.0  (n=7001) | F4b_P5_traces.csv:lam1.0_f0.1_mean/_lo/_hi | computed | L722 '(b) active fraction A(t) at lambda=1,2 for f=0.01,0.10' |
| (b) trace lam2.0_f0.01 mean and band | mean 0.0100236 … 0.500636  (n=7001) | F4b_P5_traces.csv:lam2.0_f0.01_mean/_lo/_hi | computed | L722 '(b) active fraction A(t) at lambda=1,2 for f=0.01,0.10' |
| (b) trace lam2.0_f0.1 mean and band | mean 0.0999702 … 0.50057  (n=7001) | F4b_P5_traces.csv:lam2.0_f0.1_mean/_lo/_hi | computed | L722 '(b) active fraction A(t) at lambda=1,2 for f=0.01,0.10' |
| (b) reference line / label '$A^*=1/2$' | 0.5 | theory: class-1 stationary activity | transcribed | L722 'settles at A^*=1/2 at lambda=2' |
| (b) shaded 'measurement window [20,70]' | 20, 70 | design measurement window | transcribed | L722 'measured over [20,70]' |
| (b) band note 'across 50 replicates' | 50 | design replicate count | transcribed | L722 'Panel (b) uses N=10^5 and 50 replicate trajectories' |
| (b) panel label 'alpha=2, c_b=0.5, r=1, N=10^5' | 2, 0.5, 1, 100000 | design parameters (Sec. V-E) | transcribed | L722 '(b) Class-1 example at alpha=2' and 'Panel (b) uses N=10^5' |
| (b) legend 'lambda=1/2, f=0.01/0.10' | 1, 2, 0.01, 0.10 | design parameters; F4b_P5_traces.csv column names | transcribed | L722 'at lambda=1,2 for f=0.01,0.10' |
