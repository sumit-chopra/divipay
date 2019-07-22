from enum import Enum

class ControlOperator(Enum):
    IN = 1
    EQ = 2 
    LTE = 3
    GTE = 4
    LT = 5
    GT = 6
        
class ControlOperation(object):
    def __init__(self, control_operator):
            self.control_operator = control_operator
    def factory(control_operator):
        if control_operator == ControlOperator.IN:
                return InControlOperator(control_operator)
        if control_operator == ControlOperator.EQ:
                return EqualControlOperator(control_operator)
        if control_operator == ControlOperator.LTE:
                return LessThanEqualControlOperator(control_operator)
        if control_operator == ControlOperator.GTE:
                return GreaterThanEqualControlOperator(control_operator)
        if control_operator == ControlOperator.GT:
                return GreaterThanControlOperator(control_operator)
        if control_operator == ControlOperator.LT:
                return LessThanEqualControlOperator(control_operator)
        assert 0, "Bad Control Operation Creation: " + type
    factory = staticmethod(factory)
        
class InControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 in op2

                    
class EqualControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 == op2
        
class LessThanEqualControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 <= op2
        
class GreaterThanEqualControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 >= op2
        
class LessThanControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 < op2        

class GreaterThanControlOperator(ControlOperation):
        def process(self, op1, op2):
            return op1 > op2
                