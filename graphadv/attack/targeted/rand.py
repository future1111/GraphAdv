import random
import numpy as np
from graphadv.attack.targeted.targeted_attacker import TargetedAttacker
from graphgallery import tqdm


class RAND(TargetedAttacker):
    def __init__(self, adj, seed=None, name=None, **kwargs):
        super().__init__(adj, seed=seed, name=name, **kwargs)
        self.nodes_set = set(range(self.n_nodes))

    def reset(self):
        super().reset()
        self.structure_flips = {}
        self.modified_degree = self.degree.copy()

    def attack(self, target, n_perturbations=None, threshold=0.5, direct_attack=True,
               structure_attack=True, feature_attack=False, disable=False):

        super().attack(target, n_perturbations, direct_attack, structure_attack, feature_attack)

        if direct_attack:
            influencer_nodes = [target]
        else:
            influencer_nodes = self.adj[target].indices.tolist()

        chosen = 0
        structure_flips = self.structure_flips

        with tqdm(total=self.n_perturbations, desc='Peturbing Graph', disable=disable) as pbar:
            while chosen < self.n_perturbations:

                # randomly choose to add or remove edges
                if np.random.rand() <= threshold:
                    delta = 1.0
                    edge = self.add_an_edge(influencer_nodes)
                else:
                    delta = -1.0
                    edge = self.del_an_edge(influencer_nodes)

                if edge is not None:
                    chosen += 1
                    structure_flips[edge] = chosen
                    u, v = edge
                    self.modified_degree[u] += delta
                    self.modified_degree[v] += delta
                    pbar.update(1)

    def add_an_edge(self, influencer_nodes):
        u = random.choice(influencer_nodes)
        neighbors = self.adj[u].indices.tolist()
        potential_nodes = list(self.nodes_set - set(neighbors) - set([self.target, u]))

        if len(potential_nodes) == 0:
            return None

        v = random.choice(potential_nodes)

        if not self.is_modified_edge(u, v):
            return (u, v)
        else:
            return None

    def del_an_edge(self, influencer_nodes):

        u = random.choice(influencer_nodes)
        neighbors = self.adj[u].indices.tolist()
        potential_nodes = list(set(neighbors) - set([self.target, u]))

        if len(potential_nodes) == 0:
            return None

        v = random.choice(potential_nodes)

        if not self.allow_singleton and (self.modified_degree[u] <= 1 or self.modified_degree[v] <= 1):
            return None

        if not self.is_modified_edge(u, v):
            return (u, v)
        else:
            return None
