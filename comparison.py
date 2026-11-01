"""Independent synthetic benchmark; final test never enters model selection."""
from dataclasses import asdict
import json
import math
import random
from pathlib import Path
import sys
from scipy.integrate import solve_ivp
from roboidf.core import Dataset, Parameters, fit, IdentificationError
from roboidf.backends import FitConfig, fit_bounded, select_excitation

TRUTH = Parameters(2., .4)
LIMIT = .025

def _effort(seed, samples=240, dt=.025):
    rng=random.Random(seed)
    phase=rng.uniform(0,2*math.pi)
    return tuple(2*math.sin(.9*i*dt+phase)+math.sin(2.3*i*dt+.3*phase) for i in range(samples))

def generate(scenario, split, seed, train_effort=None):
    """Bench owns ground truth and generator; Core sees only Dataset."""
    dt=.025
    u=tuple(train_effort) if train_effort is not None else _effort(seed)
    if scenario=='zero-excitation': u=(0.,)*(len(u)+(0 if split=='train' else 1))
    v=[0.]; rng=random.Random(seed+10000)
    for force in u:
        if scenario=='continuous':
            sol=solve_ivp(lambda t,y:[(force-.4*y[0])/2.], (0,dt),[v[-1]],rtol=1e-10,atol=1e-12)
            if not sol.success: raise RuntimeError(sol.message)
            v.append(float(sol.y[0,-1]))
        else:
            # Unmodeled position spring creates a structural mismatch.
            position=sum(v)*dt if scenario=='mismatch' else 0.
            v.append(v[-1]+dt*(force-.4*v[-1]-3.*position)/2.)
    if scenario=='noise': v=[x+rng.gauss(0,.01) for x in v]
    return Dataset(dt,tuple(v),u,split,seed)

def evaluate(model, data):
    """Independent free-rollout scorer, not Core's acceptance flag."""
    velocity=data.velocity[0]; squared=[]
    for force,observed in zip(data.effort,data.velocity[1:]):
        velocity+=data.dt*(force-model.damping*velocity)/model.mass
        squared.append((velocity-observed)**2)
    value=math.sqrt(sum(squared)/len(squared))
    if not math.isfinite(value): raise ValueError('nonfinite test metric')
    return value

def run_comparison(test_seed=501):
    if type(test_seed) is not int or test_seed in (101, 202):
        raise ValueError("final test seed must differ from train and validation")
    candidates={'smooth':_effort(101),'alternating':tuple(2*(-1)**i for i in range(240)), 'zero':(0.,)*240}
    selection=select_excitation(candidates,Parameters(1.5,.6),.025,max_effort=4,max_slew=200,max_candidates=3)
    training=candidates[selection['selected']]
    report={'schema_version':'comparison.v1','scope':'offline-synthetic-scalar-only',
            'test_policy':'fixed final test; no fitting, tuning, or excitation selection feedback',
            'selection':selection,'threshold_rmse_m_s':LIMIT,'cases':[]}
    for scenario in ('clean','noise','mismatch','zero-excitation','continuous'):
        train=generate(scenario,'train',101,training)
        validation=generate(scenario,'validation',202)
        # Model fitting and validation are finished before constructing final test.
        optimized=fit_bounded(train,validation,FitConfig(validation_rmse_limit=LIMIT))
        baseline={'backend':'m0-linear-least-squares','model':None,'failure':None,'passed':False,'test_rmse_m_s':None}
        baseline_model=None
        try:
            baseline_model=fit(train)
            baseline['model']=asdict(baseline_model)
            baseline['validation_rmse_m_s']=evaluate(baseline_model,validation)
            if baseline['validation_rmse_m_s']>LIMIT: baseline['failure']='VALIDATION_FAILED'
        except (IdentificationError,ValueError) as exc: baseline['failure']=str(exc)
        test=generate(scenario,'test',test_seed)
        scipy_result={'fit':optimized,'passed':False,'test_rmse_m_s':None,'parameter_relative_error':None}
        if optimized['model'] is not None:
            model=Parameters(**optimized['model'])
            error=evaluate(model,test); scipy_result['test_rmse_m_s']=error
            scipy_result['passed']=optimized['status']=='VALIDATED' and error<=LIMIT
            scipy_result['parameter_relative_error']={'mass':abs(model.mass/TRUTH.mass-1),'damping':abs(model.damping/TRUTH.damping-1)}
        if baseline_model is not None:
            baseline['test_rmse_m_s']=evaluate(baseline_model,test)
            baseline['passed']=baseline['failure'] is None and baseline['test_rmse_m_s']<=LIMIT
            baseline['parameter_relative_error']={'mass':abs(baseline_model.mass/TRUTH.mass-1),'damping':abs(baseline_model.damping/TRUTH.damping-1)}
        report['cases'].append({'scenario':scenario,'generator':'scipy.solve_ivp-continuous' if scenario=='continuous' else 'bench-independent-euler',
                                'noise_std_m_s':.01 if scenario=='noise' else 0.,'truth':asdict(TRUTH),
                                'seeds':{'train':101,'validation':202,'test':test_seed},
                                'data_hashes':{'train':train.digest(),'validation':validation.digest(),'test':test.digest()},
                                'baseline':baseline,'scipy':scipy_result})
    return report

def main():
    report=run_comparison()
    payload=json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/comparison.json').write_text(payload+'\n',encoding='utf-8')
    print(payload)
    cases={x['scenario']:x for x in report['cases']}
    return 0 if (cases['clean']['scipy']['passed'] and cases['clean']['baseline']['passed']
                 and not cases['mismatch']['scipy']['passed'] and not cases['zero-excitation']['scipy']['passed']) else 1

if __name__=='__main__': sys.exit(main())
