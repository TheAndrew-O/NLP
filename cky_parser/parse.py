import sys

class Node:
    def __init__(self, parent, left_child, bottom_child=None):
        self.parent = parent
        self.left_child = left_child
        self.bottom_child = bottom_child

class CKY_Parser:
    global rules_list
    rules_list = {}
    def __init__(self, cfg, sentence):
        self.sentence = sentence
        self.cky_table = None
        self.cnf = None
        self.cfg_to_cnf(cfg)
    
    def create_rule(self,rules):
        #rule[0] represents lefthand side
        #rule[1..n] represent right hand side
        if(rules[0] not in rules_list):
            rules_list[rules[0]] = []
        #Add right hand rules
        rules_list[rules[0]].append(rules[1:])
    
    def read_grammar_file(self,grammar_file):
        with open(grammar_file) as fp:
            lines = fp.readlines()
        #Remove comments
        for elem in lines:
            if elem[0] == "#":
                lines.remove(elem)
        #Remove arrows. Return list of rules. Each rule is a list of symbols/terminals.
        return [line.replace("->","").split() for line in lines]
    
    def cfg_to_cnf(self,grammar_file):
        cfg = self.read_grammar_file(grammar_file)
        count = 0
        units = []
        result = []
        temp = result.append
        #iterate through rules in cfg, convert to cnf
        for rule in cfg:
            rules = []
            #One nonterminal symbol on right hand side
            if(len(rule) == 2 and (rule[1][0].islower() != True)):
                units.append(rule)
                self.create_rule(rule)
                continue
            #two symbols on right hand side
            elif(len(rule) > 2):
                #Get a list of the terminals
                t = []
                for rul, cond in enumerate(rule):
                    if(cond[0].islower()):
                        t.append(cond,rul)
                #if terminals are present in given rule, create a new nonterminal symbol 
                if(len(t) != 0):
                    for elem in t:
                        #Add counter to the end of the given nonterminal symbol to create new nonterminal symbol
                        rule[elem[1]] = (rule[0] + str(count))
                        rules += [(rule[0] + str(count)), elem[0]]
                    count += 1
                while(len(rule) > 3):
                    #Create new symbols for rules that have a right hand side greater than 2
                    rules += [(rule[0] + str(count)), rule[1], rule[2]]
                    #create new rule for 3rd+ symbol on right hand side
                    rule = [rule[0]] + [rule[0] + str(count)] + rule[3:]
                    count += 1
            #add rule to global rule dict
            self.create_rule(rule)
            #extend rule recursively, such that last elem is the list itself
            temp(rule)
            if(len(rules) != 0):
                temp(rules)

        while(units):
            #If the rule has only a single nonterminal symbol on right hand side
            rule = units.pop()
            #check if first symbol on right hand side exists in rules
            if(rule[1] in rules_list):
                #Iterate over right hand side
                for elem in rules_list[rule[1]]:
                    rules = [rule[0]] + elem
                    if(len(rules) > 2 or rules[1][0].islower()):
                        if(rules not in result):
                            temp(rules)
                        else:
                            units.append(rules)
                        self.create_rule(rules)
        self.cnf = result
    
    def cky_parse(self):
        length = len(self.sentence)
        self.cky_table = []
        #Create cky table, each cell is a node that will point to another cell
        for i in range(length):
            temp = []
            for j in range(length):
                temp.append([])
            self.cky_table.append(temp)
        
        word_index = enumerate(self.sentence)
        #for j←from 1 to LENGTH(words) do table[ j−1, j]←{A | A → words[ j] ∈ grammar} 
        for index, word in word_index:
            for rule in self.cnf:
                if(word == rule[1]):
                    terminal = Node(rule[0], word)
                    self.cky_table[index][index].append(terminal)
            #Given index, iterate over the rows: for i←from j−2 downto 0 do
            for j in range(index - 1, -1, -1):
                #for k←i+1 to j−1 do
                for k in range(j, index):
                    left_cell = self.cky_table[j][k]
                    bottom_cell = self.cky_table[k + 1][index]
                    #Fill the cells in cky table
                    for rule in self.cnf:
                        left_node = []
                        #Fill left cells
                        for node in left_cell:
                            if(node.parent == rule[1]):
                                left_node.append(node)
                        if(len(left_node) != 0):
                            bottom_node = []
                            #Fill bottom cells
                            for node in bottom_cell:
                                if(node.parent == rule[2]):
                                    bottom_node.append(node)
                            #table[i,j] ← table[i,j] ∪ 
                            #                  {A | A → BC ∈ grammar, 
                            #                   B ∈ table[i,k], 
                            #                   C ∈ table[k, j]}
                            temp = []
                            for left_child in left_node:
                                for bottom_child in bottom_node:
                                    temp.append(Node(rule[0], left_child, bottom_child))#Fill cky_table with pointers to the rules
                            
                            self.cky_table[j][i].extend(temp)

    def print_tree(self):
        first_rule = self.cnf[0]
        last_rule = []
        #Check far right corner/top cell of cky table for starting point
        for node in self.cky_table[0][-1]:
            #If the left hand rule from CKY table matches the left hand rule of the first rule in CNF
            #Add to list of possible parse trees
            if node.parent == first_rule[0]:
                last_rule.append(node)
        
        #If rule exists in top right corner of cky table, then legal parse exists
        if(len(last_rule) != 0):
            print("Parses Found:")
            trees = []
            for node in last_rule:
                temp = tree_traversal(node)
                trees.append(temp)
            for tree in trees:
                print(tree)
        else:
            print("Sentence does not exist in this grammar.")

def tree_traversal(node):
    if(node.bottom_child == None):
        return "(" + node.parent + " " + node.left_child + ")"
    #Preorder tree traversal, first print node, then recur on left child, then recur on right child
    return "(" + node.parent + " " + tree_traversal(node.left_child) + " " + tree_traversal(node.bottom_child) + ")"

def main():
    grammar_file = sys.argv[1]
    sentence = sys.argv[2]
    #Split sentence into list of words
    p = CKY_Parser(grammar_file, list(sentence.split(" ")))
    p.cky_parse()
    p.print_tree()

if __name__ == '__main__':
    main()