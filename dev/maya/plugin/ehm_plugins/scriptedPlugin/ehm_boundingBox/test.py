import numpy as np

poses_list1 = [ [-0.2, 0.7, -0.7],
                [-0.5, 1.5, -1.5],
                [-0.7, 2.3, -2.2] ]


poses_list2 = [ [-0.3, 0.7, -0.7],
                [-0.5, 1.5, -1.5],
                [-0.7, 2.3, -2.2] ]
                
for poses_list in (poses_list1, poses_list2):
    poses_matrix = np.matrix( poses_list ).T
    poses_cov = np.cov( poses_matrix )
    eig_value, eig_matrix = np.linalg.eig( poses_cov )
    print "-----"
    print eig_matrix


"""
-----
[[-0.22274715  0.72944023 -0.64676167]
 [ 0.7109161   0.57549944  0.40422604]
 [-0.66706972  0.36975308  0.64676167]]
-----
[[ -1.79370029e-01   9.70142500e-01  -1.63248039e-01]
 [  7.17480116e-01   2.42535625e-01   6.52992154e-01]
 [ -6.73088906e-01   3.39954799e-14   7.39561576e-01]]

"""