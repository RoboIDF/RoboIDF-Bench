"""Independent deterministic M0 evaluation; no training feedback from test data."""
import json
import math
import random
from pathlib import Path
from dataclasses import asdict
from roboidf import Dataset, Parameters, fit, IdentificationError

PARAMETER_TOLERANCE=1e-7
ROLLOUT_TOLERANCE=1e-8

def generate(truth,seed,split):
    rng=random.Random(seed); dt=.01; velocities=[.3]
    forces=[3*math.sin(k*.071)+rng.uniform(-1,1) for k in range(600)]
    a=1-dt*truth.damping/truth.mass; b=dt/truth.mass
    for force in forces:
        velocities.append(a*velocities[-1]+b*force)
    return Dataset(dt,tuple(velocities),tuple(forces),split,seed)

def evaluate(model,truth,seed):
    test=generate(truth,seed,'test')
    # Independent metric implementation: free rollout, no Core evaluator reuse.
    prediction=test.velocity[0]; residuals=[]
    model_record=asdict(model); truth_record=asdict(truth)
    for i,force in enumerate(test.effort):
        prediction=(1-test.dt*model.damping/model.mass)*prediction+test.dt*force/model.mass
        residual=prediction-test.velocity[i+1]
        if not math.isfinite(residual):
            return {'passed':False,'reason':'DIVERGENT_ROLLOUT','model':model_record,
                    'truth':truth_record,'test_seed':seed,'test_sha256':test.digest()}
        residuals.append(residual)
    rmse=math.hypot(*residuals)/math.sqrt(len(residuals))
    # Relative to a declared floor for zero-valued parameters.
    errors={key:abs(model_record[key]-value)/max(abs(value),1e-12)
            for key,value in truth_record.items()}
    return {'test_seed':seed,'test_sha256':test.digest(),'parameter_relative_error':errors,
            'model':model_record,'truth':truth_record,
            'rollout_rmse_m_s':rmse,'passed':max(errors.values())<=PARAMETER_TOLERANCE and rmse<=ROLLOUT_TOLERANCE}

def suite():
    cases=[]
    for i,truth in enumerate([Parameters(1,.2),Parameters(2,.4),Parameters(4,1.2)]):
        train=generate(truth,100+i,'train')
        model=fit(train)
        case=evaluate(model,truth,900+i)
        case.update(train_seed=100+i,train_sha256=train.digest())
        cases.append(case)
    rejected=False
    try:
        fit(Dataset(.01,(0.,)*21,(0.,)*20,'train',0))
    except IdentificationError as exc:
        rejected='UNIDENTIFIABLE' in str(exc)
    return {'schema_version':'m0.v1','suite':'synthetic-noiseless-v1',
            'thresholds':{'parameter_relative_error':PARAMETER_TOLERANCE,'rollout_rmse_m_s':ROLLOUT_TOLERANCE},
            'cases':cases,'zero_excitation_rejected':rejected,'passed':rejected and all(c['passed'] for c in cases)}

if __name__=='__main__':
    result=suite(); path=Path('artifacts/bench.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result['passed'] else 1)
