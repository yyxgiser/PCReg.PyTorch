import math
import numpy as np
import torch


def pc_normalize(pc):
    mean = np.mean(pc, axis=0)
    pc -= mean
    m = np.max(np.sqrt(np.sum(np.power(pc, 2), axis=1)))
    pc /= m
    return pc


def random_select_points(pc, m):
    if m < 0:
        idx = np.arange(pc.shape[0])
        np.random.shuffle(idx)
        return pc[idx, :]
    n = pc.shape[0]
    replace = False if n >= m else True
    idx = np.random.choice(n, size=(m, ), replace=replace)
    return pc[idx, :]


def generate_rotation_x_matrix(theta):
    mat = np.eye(3, dtype=np.float32)
    mat[1, 1] = math.cos(theta)
    mat[1, 2] = -math.sin(theta)
    mat[2, 1] = math.sin(theta)
    mat[2, 2] = math.cos(theta)
    return mat


def generate_rotation_y_matrix(theta):
    mat = np.eye(3, dtype=np.float32)
    mat[0, 0] = math.cos(theta)
    mat[0, 2] = math.sin(theta)
    mat[2, 0] = -math.sin(theta)
    mat[2, 2] = math.cos(theta)
    return mat


def generate_rotation_z_matrix(theta):
    mat = np.eye(3, dtype=np.float32)
    mat[0, 0] = math.cos(theta)
    mat[0, 1] = -math.sin(theta)
    mat[1, 0] = math.sin(theta)
    mat[1, 1] = math.cos(theta)
    return mat


def generate_random_rotation_matrix(angle1=-45, angle2=45):
    thetax, thetay, thetaz = np.random.uniform(angle1, angle2, size=(3,))
    matx = generate_rotation_x_matrix(thetax / 180 * math.pi)
    maty = generate_rotation_y_matrix(thetay / 180 * math.pi)
    matz = generate_rotation_z_matrix(thetaz / 180 * math.pi)
    return np.dot(matz, np.dot(maty, matx))


def generate_random_tranlation_vector(range1=-1, range2=1):
    tranlation_vector = np.random.uniform(range1, range2, size=(3, )).astype(np.float32)
    return tranlation_vector


def transform(pc, R, t):
    return np.dot(pc, R.T) + t


def batch_transform(batch_pc, batch_R, batch_t):
    '''

    :param batch_pc: shape=(B, N, 3)
    :param batch_R: shape=(B, 3, 3)
    :param batch_t: shape=(B, 3)
    :return: shape(B, N, 3)
    '''
    transformed_pc = torch.matmul(batch_pc, batch_R.permute(0, 2, 1).contiguous()) \
                    + torch.unsqueeze(batch_t, 1)
    return transformed_pc


# The transformation between unit quaternion and rotation matrix is referenced to
# https://zhuanlan.zhihu.com/p/45404840

def quat2mat(quat):
    w, x, y, z = quat
    R = np.zeros((3, 3), dtype=np.float32)
    R[0][0] = 1 - 2*y*y - 2*z*z
    R[0][1] = 2*x*y - 2*z*w
    R[0][2] = 2*x*z + 2*y*w
    R[1][0] = 2*x*y + 2*z*w
    R[1][1] = 1 - 2*x*x - 2*z*z
    R[1][2] = 2*y*z - 2*x*w
    R[2][0] = 2*x*z - 2*y*w
    R[2][1] = 2*y*z + 2*x*w
    R[2][2] = 1 - 2*x*x - 2*y*y
    return R


def batch_quat2mat(batch_quat):
    '''

    :param batch_quat: shape=(B, 4)
    :return:
    '''
    w, x, y, z = batch_quat[:, 0], batch_quat[:, 1], batch_quat[:, 2], \
                 batch_quat[:, 3]
    device = batch_quat.device
    B = batch_quat.size()[0]
    R = torch.zeros(dtype=torch.float, size=(B, 3, 3)).to(device)
    R[:, 0, 0] = 1 - 2 * y * y - 2 * z * z
    R[:, 0, 1] = 2 * x * y - 2 * z * w
    R[:, 0, 2] = 2 * x * z + 2 * y * w
    R[:, 1, 0] = 2 * x * y + 2 * z * w
    R[:, 1, 1] = 1 - 2 * x * x - 2 * z * z
    R[:, 1, 2] = 2 * y * z - 2 * x * w
    R[:, 2, 0] = 2 * x * z - 2 * y * w
    R[:, 2, 1] = 2 * y * z + 2 * x * w
    R[:, 2, 2] = 1 - 2 * x * x - 2 * y * y
    return R


def mat2quat(mat):
    w = math.sqrt(mat[0, 0] + mat[1, 1] + mat[2, 2] + 1) / 2
    x = (mat[2, 1] - mat[1, 2]) / (4 * w)
    y = (mat[0, 2] - mat[2, 0]) / (4 * w)
    z = (mat[1, 0] - mat[0, 1]) / (4 * w)
    return w, x, y, z


def jitter_point_cloud(pc, sigma=0.01, clip=0.05):
    N, C = pc.shape
    assert(clip > 0)
    jittered_data = np.clip(sigma * np.random.randn(N, C), -1*clip, clip).astype(np.float32)
    jittered_data += pc
    return jittered_data


def shift_point_cloud(pc, shift_range=0.1):
    N, C = pc.shape
    shifts = np.random.uniform(-shift_range, shift_range, (1, C)).astype(np.float32)
    pc += shifts
    return pc


def random_scale_point_cloud(pc, scale_low=0.8, scale_high=1.25):
    scale = np.random.uniform(scale_low, scale_high, 1)
    pc *= scale
    return pc
