#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from accessify import private
from random import uniform, choices

import networkx as nx

@dataclass
class ACOData(object):
	"""data class for ACO_algorithm class"""
	
	ALPHA: float = 1.0
	BETA: float = 1.0
	PE: float = 0.25

	MIN_ROAD: float = 0.0

	@private
	def validate(self) -> bool:
		valid = True

		for field_name, field_def in self.__dataclass_fields__.items():
			actual_type = type(getattr(self, field_name)) 
			if actual_type != field_def.type:
				print(f"\t{field_name}: '{actual_type}' instead of '{field_def.type}'")
				valid = False

		return valid

	def __post_init__(self) -> None:
		
		if not self.validate():
			raise TypeError

	def __repr__(self) -> str:

		kws_values = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		kws_values = '\n\t'.join(kws_values)

		kws_types = ""
		for field_name, field_def in self.__dataclass_fields__.items():
			kws_types += f"\n\t{field_name}: {field_def.type}'"
		
		return f"\n-constants-values\n\n\t{kws_values}\n\n-constants-types\n{kws_types}"

class ACOAlgorithm(nx.Graph):
	"""docstring for ACOAlgorithm will be soon"""

	def __init__(self, kwargs = {}):
		super(ACOAlgorithm, self).__init__()
	
		self._args = ACOData(**kwargs)

	def GenStandartACOGraph(self, node_count: int) -> None:
		
		for node in range(node_count):
			self.add_node(node) 

		for node_i in list(self.nodes()):
			for node_j in list(self.nodes())[node_i+1::]:

				self.add_edge(node_i, node_j)
				self[node_i][node_j]["weight"] = 0.5 # randomaze!!
				self[node_i][node_j]["lenght"] = round(node_i+1, 4)  # randomaze!!
				self[node_i][node_j]["valid"] = True

	def GenRandomACOGraph(self, node_count: int) -> None:

		for node in range(node_count):
			self.add_node(node)


	@private
	def P(self, vertex_i: int) -> list:

		selected_edges = [(i,j,e) for i,j,e in self.edges(data=True) if i == vertex_i or j == vertex_i]
		selected_edges = [(i,j,e) for i,j,e in selected_edges if e['valid'] == True]

		transition_force_list = []
		transition_force_summ = 0
		for i, j, e in selected_edges: 
			transition_force = (self.edges[i, j]['weight'] * self._args.ALPHA 
								+ (1 / self.edges[i, j]['lenght'])* self._args.ALPHA)
			
			if i == vertex_i:
				transition_force_list.append((i, j, transition_force)) 
			else:
				transition_force_list.append((j, i, transition_force)) 

			transition_force_summ += transition_force

			
			probability_list = list(map(lambda x: (x[1], x[2] / transition_force_summ), transition_force_list))

		return list(probability_list)

	@private
	def choice_next_vertex(self, probability_list: list) -> int:
		next_vertex ,= choices(
			list(map(lambda x: x[0], probability_list)),
			weights = list(map(lambda x: x[1], probability_list))
			)
		return next_vertex

	def GenerateSolutions(self, iterations: int) -> list:

		solutions=[]
		for iteration in range(iterations):
			start_vertex = iteration % self.number_of_nodes() 


			solution = [start_vertex]

			curent_vertex = start_vertex
			for i in range(self.number_of_nodes() - 1):

				probs = self.P(curent_vertex)
				next_vertex = self.choice_next_vertex(probs)

				for i,j,e in self.edges(data=True):
					if i == curent_vertex or j == curent_vertex:
						self[i][j]['valid'] = False

				solution.append(next_vertex)
				curent_vertex = next_vertex

			for (i,j,e) in self.edges(data=True): e['valid'] = True
			solutions.append(solution)

		yield solutions

	def PheromoneUpdate(self, solutions: list) -> None:
		
		for (i,j,e) in self.edges(data=True): e['weight'] = e['weight'] * (1 - self._args.PE)

		for solution in next(solutions):
			slices = [solution[::1], solution[1::]]
			
			min_road = 0
			length = 0

			for s1, s2 in zip(slices[0], slices[1]):
				length += self[s1][s2]['lenght']
			print(solution, length)	

	def __repr__(self):

		graph = "\n\t".join([f"{x}" for x in list(self.edges(data=True))])
		return f"\n-Graph edges\n\n\t{graph}\n{self._args}" # self agrs call to own repr in ACO_data class 

if __name__ == '__main__':
	obj = ACOAlgorithm({"ALPHA": 1.0, "BETA": 5.0})
	obj.GenStandartACOGraph(5)
	t = obj.GenerateSolutions(20)
	#print(next(t))
	obj.PheromoneUpdate(t)
	print(repr(obj))

	