"""Regression checks of wrapper semantics; not additional research episodes."""
from pathlib import Path
import importlib.util,json,sys
import numpy as np
OP=Path('/workspace/recovery/operations')
spec=importlib.util.spec_from_file_location('approved_driver_test',OP/'proposals/run_amended_dense_merge.py');driver=importlib.util.module_from_spec(spec);sys.modules[spec.name]=driver;spec.loader.exec_module(driver)
pre=json.loads((OP/'proposals/INITIALIZATION_AMENDMENT_PREFLIGHT.json').read_text())
seeds=[r['seed'] for r in pre['results'] if r['identical_to_original_when_original_accepts']][:3]
def state(env):return np.array([[*v.position,v.heading,v.velocity,v.desired_speed] for v in [env.ego,*env.npcs]])
steps=0
for seed in seeds:
 for delay in [0,5,10]:
  old=driver.core.StressEnv('merge',delay,'denser_traffic');new=driver.AmendedMergeEnv('merge',delay,'denser_traffic')
  a,_=old.reset(seed=seed);b,_=new.reset(seed=seed)
  np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(state(old),state(new))
  for i in range(20):
   action=np.array([.1*np.cos(i),.05*np.sin(i)],dtype=np.float32)
   a,ra,da,ta,ia=old.step(action);b,rb,db,tb,ib=new.step(action)
   np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(state(old),state(new));assert (ra,da,ta)==(rb,db,tb)
   for field in ['collision','success','lateral_error']:assert ia[field]==ib[field]
   steps+=1
   if da or ta:break
  old.close();new.close()
try:driver.AmendedMergeEnv('highway',0,'denser_traffic')
except AssertionError:pass
else:raise AssertionError('Scope guard did not reject highway')
try:driver.AmendedMergeEnv('merge',0,'weaker_actuation')
except AssertionError:pass
else:raise AssertionError('Scope guard did not reject weaker actuation')
result=dict(status='PASS',original_success_seeds=seeds,delays_in_steps=[0,5,10],paired_initializations=9,identical_step_transitions=steps,scope_guards_passed=2,scope='Diagnostic equivalence of original and amended wrappers on original-accepted states; not new experiment evidence')
(OP/'AMENDED_DYNAMICS_REGRESSION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
