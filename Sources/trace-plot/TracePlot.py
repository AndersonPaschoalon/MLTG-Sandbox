from Database import  PacketTable


class TracePlot:

    def __init__(self, flow_database, name, plot_color):
        self.pt = PacketTable(database_file=flow_database, trace_name=name)
        self.name = name
        self.plot_color = plot_color

    def load(self, cols):
        return self.pt.fetch(column=cols)




