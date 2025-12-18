# conveyor/interface.py
class ConveyorInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def update(self, config, status):
        # Update conveyor visualization
        pass
    
    def write_gui_to_status(self, status):
        # Write GUI controls to simulation
        pass