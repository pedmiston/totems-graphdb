import pandas

from graph.graph_db import connect_to_graph_db

class Landscape:
    """Provide an interface to the Neo4J database containing the landscape."""
    def __init__(self):
        """Copies the landscape for faster lookups."""
        self.graph = connect_to_graph_db()
        recipes = pandas.DataFrame(self.graph.data("""
        MATCH (recipe) -[:CREATES]-> (result:Item)
        MATCH (result) -[:INHERITS]-> (requirement:Item)
        RETURN result.label as result_label,
               result.number as result_number,
               requirement.label as requirement_label,
               requirement.number as requirement_number;
        """))

        if len(recipes) == 0:
            raise LandscapeNotInitialized

        # Convert int64 to int
        for numeric_col in ['result_number', 'requirement_number']:
            recipes[numeric_col] = recipes[numeric_col].astype(int)

        result_vars = ['result_label', 'result_number']
        self.answer_key_labels = {}
        self.answer_key_numbers = {}
        for (label, number), chunk in recipes.groupby(result_vars):
            requirement_labels = frozenset(chunk.requirement_label.tolist())
            requirement_numbers = frozenset(
                [int(r) for r in chunk.requirement_number.tolist()]
            )
            self.answer_key_labels[requirement_labels] = label
            self.answer_key_numbers[requirement_numbers] = int(number)

        self.max_items = self.graph.data("""
        MATCH (n:Item)
        RETURN count(n) as n_items
        """)[0]['n_items']  # graph.data always returns a list

        self.adjacent_recipes = {}

        self.labels = pandas.DataFrame(self.graph.data("""
        MATCH (n:Item)
        RETURN n.number as number, n.label as label
        """)).set_index('number').squeeze().to_dict()

        # self.item_numbers = {label: number for number, label in self.labels}

        self.scores = None

    def starting_inventory(self):
        return set([1, 2, 3, 4, 5, 6])

    def get_label(self, item_number):
        return self.labels.get(item_number)

    def get_score(self, item_number):
        if self.scores is None:
            self.scores = pandas.DataFrame(self.graph.data("""
            MATCH (n:Item)
            RETURN n.number as number, n.score as score
            """)).set_index('number').squeeze().to_dict()
        return self.scores.get(item_number, 0)


    # def get_number(self, label):
    #     return self.item_numbers[label]

    def evaluate(self, guess):
        return self.evaluate_labels(guess) or self.evaluate_numbers(guess)

    def evaluate_labels(self, guess_labels):
        return self.answer_key_labels.get(frozenset(guess_labels))

    def evaluate_numbers(self, guess_numbers):
        return self.answer_key_numbers.get(frozenset(guess_numbers))

    def evaluate_guesses(self, guesses):
        new_items = {}
        for guess in guesses:
            result = self.evaluate(guess)
            if result:
                new_items[frozenset(guess)] = result
        return new_items

    def adjacent_possible(self, inventory):
        """Return a set of recipes obtainable with the given inventory."""
        inv = frozenset(inventory)
        if inv not in self.adjacent_recipes:
            self.adjacent_recipes[inv] = self._adjacent_possible(inv)
        return self.adjacent_recipes[inv]

    def _adjacent_possible(self, inventory):
        inventory_type = "label"
        if isinstance(list(inventory)[0], int):
            inventory_type = "number"

        adjacent_query = """
        MATCH (n:Item) <-[:REQUIRES]- (r:Recipe)
        WHERE n.{type} IN {inventory}
        RETURN r.code as code
        """.format(inventory=list(inventory), type=inventory_type)
        adjacent_recipes = pandas.DataFrame(self.graph.data(adjacent_query))

        requirements_query = """
        MATCH (r:Recipe) -[:REQUIRES]-> (required:Item)
        MATCH (r) -[:CREATES]-> (created:Item)
        WHERE r.code IN {codes} AND NOT created.{type} IN {inventory}
        RETURN r.code as code, required.{type} as requirement
        """.format(codes=adjacent_recipes.code.tolist(),
                   inventory=list(inventory),
                   type=inventory_type)
        requirements = pandas.DataFrame(self.graph.data(requirements_query))

        adjacent_possible = []
        for code, chunk in requirements.groupby('code'):
            if all(chunk.requirement.isin(inventory)):
                adjacent_possible.append(code)

        return adjacent_possible


class LandscapeNotInitialized(Exception):
    """Nothing in the landscape yet."""
