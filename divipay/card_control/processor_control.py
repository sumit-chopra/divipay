from enum import Enum
from django.conf import settings
from .operation_control import ControlOperation
from .errors import ControlException, ControlExceptionPayload
from .messages import Messages
from card_control.operation_control import ControlOperator

class ControlType(Enum):
    # Only two types supported for now
    String = 1
    Integer = 2
    
    
def processControls(source_data, controls):
    # Check whether mandatory controls are configured for this card are not
    mandatory_check_result = check_mandatory_controls_presence(settings.MANDATORY_CONTROLS, controls)
    if mandatory_check_result is not None:
        raise ControlException("Mandatory Control {} not configured".format(mandatory_check_result), ControlExceptionPayload(mandatory_check_result))
    
    for control in controls:
            control_def = settings.CONTROL_DEFINITION[control]
            if ControlProcessor.factory(control_def).process(controls.get(control), source_data) is not True:
                    exceptionPayload = ControlExceptionPayload(control)
                    message = Messages.Control.FAILED_TO_COMPLY + control
                    raise ControlException(message, exceptionPayload)
    return True


def check_mandatory_controls_presence(mandatory_controls_list, existing_controls_list):
    # Mandatory controls are defined as [control_1, control_2, [control_3, control_4]]
    # the controls mentioned as sub_list means either of the controls sub_list should be configured
    # e.g. control_1 and control_2 should be configured
    # It is ok if either of control_3 or control_4 is configured
    for mandatory_control in mandatory_controls_list:
        if isinstance(mandatory_control, str):
            if mandatory_control not in existing_controls_list:
                return mandatory_control
        elif isinstance(mandatory_control, list):
            result = False
            for single_mandatory_control in mandatory_control:
                if single_mandatory_control in existing_controls_list:
                    result = True
                    break
            if result == False:
                return mandatory_control
    return None


# Factory Design pattern to instantiate the right control processor basis the type of control
class ControlProcessor(object):
    def __init__(self, control_def):
        self.control_def = control_def
    def factory(control_def):
        if control_def["type"] == ControlType.String.name:
                return StringControlProcessor(control_def)
        if control_def["type"] == ControlType.Integer.name:
                return IntegerControlProcessor(control_def)
        assert 0, "Bad Control Processor Creation: " + type
    factory = staticmethod(factory)
        

class StringControlProcessor(ControlProcessor):
    
    # Processes the control and matches against the source data using the ControlOperation
    # Control Operation processes the logical comparison between two variables
    def process(self, controlValue, source_data):
            print("Processing string control {}".format(self.control_def))
            incomingValue = source_data[self.control_def["src_comparison"]["variable_name"]]
            operator = ControlOperator[self.control_def["src_comparison"]["operator"]]
            return ControlOperation.factory(operator).process(incomingValue.upper(), controlValue.upper())
        
    # Validates the value of control against the configuration
    def validate(self, value):
        
        if "input_validation" in self.control_def:
            validation_obj = self.control_def["input_validation"]
            if "choices" in validation_obj:                   
                # Checks if the input value is one of the values defined in the configuration 
                return value.upper() in [item.upper() for item in validation_obj["choices"]]
            else:
                return True
        return True
                
                    
class IntegerControlProcessor(ControlProcessor):
    # Processes the control and matches against the source data using the ControlOperation
    # Control Operation processes the logical comparison between two variables
    def process(self, controlValue, source_data):
            print("Processing integer control {}".format(self.control_def))
            incomingValue = source_data[self.control_def["src_comparison"]["variable_name"]]
            try:
                    intIncomingValue = int(incomingValue)
                    intControlValue = int(controlValue)
                    operator = ControlOperator[self.control_def["src_comparison"]["operator"]]
                    return ControlOperation.factory(operator).process(intIncomingValue, intControlValue)
            except ValueError:
                    return False
    
    # Validates the value of control against the configuration
    # Converts the value to Integer and compares against the configured min_value and max_value   
    def validate(self, value):
        result = None
        try:
            int_value = int(value)
        except ValueError:
            return False
        if "input_validation" in self.control_def:
            validation_obj = self.control_def["input_validation"]
            if "min_value" in validation_obj:
                try:
                    min_value = int(validation_obj["min_value"])
                    result = (int_value >= min_value)
                except ValueError:
                    return False
                if result == False:
                    return result
            if "max_value" in validation_obj:
                try:
                    max_value = int(validation_obj["max_value"])
                    result = int_value <= max_value
                except ValueError:
                    return False
        return True if result is None else result