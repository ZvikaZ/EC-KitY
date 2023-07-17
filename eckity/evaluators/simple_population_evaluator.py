from overrides import overrides

from eckity.evaluators.individual_evaluator import IndividualEvaluator
from eckity.evaluators.population_evaluator import PopulationEvaluator
from eckity.fitness.fitness import Fitness
from eckity.individual import Individual


class SimplePopulationEvaluator(PopulationEvaluator):
	def __init__(self, executor_method='map'):
		super().__init__()
		if executor_method not in ['map', 'submit']:
			raise ValueError(f'executor_method must be either "map" or "submit", got {executor_method}')
		self.executor_method = executor_method

	@overrides
	def _evaluate(self, population):
		"""
		Updates the fitness score of the given individuals, then returns the best individual

		Parameters
		----------
		population:
			the population of the evolutionary experiment

		Returns
		-------
		individual
			the individual with the best fitness out of the given individuals
		"""
		super()._evaluate(population)
		for sub_population in population.sub_populations:
			sub_population = population.sub_populations[0]
			sp_eval: IndividualEvaluator = sub_population.evaluator

			if self.executor_method == 'submit':
				eval_futures = [self.executor.submit(sp_eval.evaluate, ind, sub_population.individuals)
		    					for ind in sub_population.individuals]
				eval_results = [future.result() for future in eval_futures]
			elif self.executor_method == 'map':
				eval_results = self.executor.map(sp_eval.evaluate, sub_population.individuals)
			
			for ind, fitness_score in zip(sub_population.individuals, eval_results):
				ind.fitness.set_fitness(fitness_score)


		# only one subpopulation in simple case
		individuals = population.sub_populations[0].individuals

		best_ind: Individual = population.sub_populations[0].individuals[0]
		best_fitness: Fitness = best_ind.fitness

		for ind in individuals[1:]:
			if ind.fitness.better_than(ind, best_fitness, best_ind):
				best_ind = ind
				best_fitness = ind.fitness

		return best_ind
