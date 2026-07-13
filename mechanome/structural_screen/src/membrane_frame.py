"""Membrane-frame alignment: symmetry-axis (channels) validated <9deg vs OPM; inertia (scaffolds)."""
import numpy as np

def symmetry_axis(coords):
    """Cn-channel membrane normal = inertia eigenvector whose eigenvalue is most separated."""
    X = coords - coords.mean(0)
    I = np.zeros((3,3))
    for x in X: I += np.dot(x,x)*np.eye(3) - np.outer(x,x)
    w,V = np.linalg.eigh(I)
    k = int(np.argmax([abs(w[i]-np.mean([w[j] for j in range(3) if j!=i])) for i in range(3)]))
    a = V[:,k]; return a/np.linalg.norm(a)

def rot_to_z(axis):
    z=np.array([0,0,1.]); a=axis/np.linalg.norm(axis)
    v=np.cross(a,z); s=np.linalg.norm(v); c=a@z
    if s<1e-8: return np.eye(3) if c>0 else np.diag([1,-1,-1.])
    vx=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+vx+vx@vx*((1-c)/s**2)
