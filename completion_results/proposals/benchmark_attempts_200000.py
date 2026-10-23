"""Traffic-v2: common, explicitly synthetic disc-vehicle benchmark."""
import sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent.parent/'submission_study'
sys.path.insert(0,str(BASE))
from extended_suite import ProtocolEnv
from scenario_config import VEHICLE

class TrafficEnv(ProtocolEnv):
    def __init__(self,scenario,delay=0,direct=False):
        self.direct=direct
        super().__init__(scenario,delay=delay)
        self.max_steps=160

    def _spawn_vehicles(self):
        # Rejection sampling preserves original straight-road distributions.
        for attempt in range(200000):
            super()._spawn_vehicles()
            if self.scenario=='roundabout':
                theta=self.roundabout_start_angle
                for j,n in enumerate(self.npcs):
                    a=theta+2*np.pi*(j+1)/(len(self.npcs)+1)+self.np_random.uniform(-.08,.08)
                    n.position=8*np.array([np.cos(a),np.sin(a)])
                    n.heading=a+np.pi/2
            if self.scenario in ('highway','merge'):
                for n in self.npcs: n.heading=0.
            vehicles=[self.ego]+self.npcs
            safe=all(np.linalg.norm(a.position-b.position)>6.0 for i,a in enumerate(vehicles) for b in vehicles[i+1:])
            if self.scenario in ('highway','merge'):
                for a in vehicles:
                    for b in vehicles:
                        dx=b.position[0]-a.position[0];dy=abs(b.position[1]-a.position[1])
                        if dx>0 and dy<4.846:
                            clearance=dx-np.sqrt(4.846**2-dy**2)
                            safe &= clearance>1.+.1*max(0.,a.velocity-b.velocity)+max(0.,a.velocity-b.velocity)**2/12.
            if safe:
                return
        raise RuntimeError('No collision-free initial traffic sample')

    def _update_dynamics(self,action):
        # Parent implements identical ego physics and command FIFO for everybody.
        npcs=self.npcs
        old_ego=self.ego.position.copy()
        self.npcs=[]
        try: super()._update_dynamics(action)
        finally: self.npcs=npcs
        vehicles=npcs+[self.ego]
        positions=[n.position.copy() for n in npcs]+[old_ego]
        updates=[]
        for i,n in enumerate(npcs):
            gap=1e6; leader_speed=n.velocity
            for j,other in enumerate(vehicles):
                if i==j: continue
                delta=positions[j]-positions[i]
                if self.scenario=='roundabout':
                    a=np.arctan2(positions[j][1],positions[j][0])-np.arctan2(positions[i][1],positions[i][0])
                    distance=8*(a%(2*np.pi))
                    # Arc length corresponding to the retained disc diameter.
                    body=16*np.arcsin(VEHICLE['b_disc']/8)
                else:
                    tangent=np.array([np.cos(n.heading),np.sin(n.heading)])
                    distance=float(delta@tangent)
                    lateral=abs(float(delta@np.array([-tangent[1],tangent[0]])))
                    if lateral>=2*VEHICLE['b_disc'] or distance<=0: continue
                    body=np.sqrt((2*VEHICLE['b_disc'])**2-lateral**2)
                candidate=distance-body
                if candidate<gap:
                    gap=candidate
                    leader_speed=max(0.,other.velocity*np.cos(other.heading-n.heading)) if self.scenario!='roundabout' else other.velocity
            # IDM: a=1.5, comfortable brake=2, standstill gap=1, headway=.6s.
            v=n.velocity
            desired=1.+max(0.,.6*v+v*(v-leader_speed)/(2*np.sqrt(3.)))
            acceleration=np.clip(1.5*(1-(v/n.desired_speed)**4-(desired/max(.1,gap))**2),-6.,1.5)
            speed=float(np.clip(v+acceleration*self.dt,0.,20.))
            if self.scenario=='roundabout':
                theta=np.arctan2(n.position[1],n.position[0])+speed*self.dt/8
                pos=8*np.array([np.cos(theta),np.sin(theta)]); heading=theta+np.pi/2
            else:
                pos=n.position+speed*self.dt*np.array([np.cos(n.heading),np.sin(n.heading)]);heading=n.heading
            updates.append((pos,heading,speed,float(acceleration)))
        for n,(pos,heading,speed,acceleration) in zip(npcs,updates):
            n.position=pos;n.heading=heading;n.velocity=speed;n.acceleration=acceleration

    def step(self,action):
        if self.direct: self.beta=1.;self.safety_enabled=False
        return super().step(action)
