import numpy as np

def angle(dim, point1, point2):
    a = np.reshape(point1, (1,dim))
    b = np.reshape(point2, (1,dim))
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    dotab = np.dot(a, np.transpose(b))
    theta = np.arccos(dotab/(norm_a*norm_b))
    return theta