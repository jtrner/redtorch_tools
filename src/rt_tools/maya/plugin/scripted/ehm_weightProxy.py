from scipy.spatial import KDTree as KDTree

tree = KDTree(([0, 0, 0], [1, 1, 2]))

query = tree.query(([2, 2, 2]), 1)
