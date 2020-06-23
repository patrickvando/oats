class Compiler_main:
    def __init__(self, filename):
        self.symbol_table = Symbol_table_stack()
        self.output_file = open(filename, 'w')
        self.ec = Expression_compiler(self.symbol_table)

    def compile_ast(self, root):
        res = []
        res += instr.HEADER
        res += instr.push(instr.BP)
        res += instr.mov(instr.BP, instr.SP)
        res += self.compile_statement_list(root)
        res += instr.mov(instr.SP, instr.BP)
        res += instr.pop(instr.BP)
        res += instr.FOOTER
        res += instr.define_print()
        self.write_instructions(res)

    def write_instructions(self, instructions):
        for instruction in instructions:
            self.output_file.write(instruction + "\n")

    def compile_statement_list(self, root):
        res = []
        res += self.allocate_variables(root)
        for statement in root.children:
            if statement.typ == "VARIABLE_DECLARATION" or statement.typ == "VARIABLE_ASSIGNMENT":
                res += self.compile_assignment(statement)
            if statement.typ == "FUNCTION_CALL":
                res += self.ec.compile_expression(statement)
        return res

    def compile_assignment(self, root):
        res = []
        variable = root.children[0]
        expression = root.children[1]
        res += self.ec.load_variable_location(variable)
        res += self.ec.compile_expression(expression)
        res += instr.pop(instr.R2)
        res += instr.pop(instr.R1)
        res += instr.mov(instr.memloc(instr.R1), instr.R2)
        return res

    def allocate_variables(self, root):
        res = []
        st = ""
        offset = 0
        variables = []
        for statement in root.children:
            if statement.typ == "VARIABLE_DECLARATION":
                info = {}
                variable = statement.children[0]
                variables.append(variable.attributes)
        for variable in variables:
            offset += 8
            variable["offset"] = offset
            self.symbol_table.insert(variable["identifier"], variable)
        #allocate space for variables
        res += instr.sub(instr.SP, offset)
        return res

from .Symbol_table import Symbol_table_stack
from .Instructions import Instructions as instr
from .Expression_compiler import Expression_compiler
