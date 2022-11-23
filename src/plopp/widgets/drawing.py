class DrawingTool:

    def __init__(self,
                 figure: View,
                 input_node: Node,
                 tool: Any,
                 func: Callable,
                 autostart=True):
        self._input_node = input_node
        self._output_nodes = {}
        self._func = func
        self._tool = tool(ax=figure.ax, autostart=autostart)
        self._tool.on_create = self.make_node
        self._tool.on_vertex_move = self.update_node
        self._tool.on_remove = self.remove_node

    def make_node(self, change: Dict[str, Any]):
        event = change['event']
        event_node = Node(lambda: change)
        # Node(
        #     func=lambda: {
        #         self._xdim:
        #         sc.scalar(event.xdata, unit=self._data_array.meta[self._xdim].unit),
        #         self._ydim:
        #         sc.scalar(event.ydata, unit=self._data_array.meta[self._ydim].unit)
        #     })
        self._event_nodes[event_node.id] = event_node
        change['artist'].nodeid = event_node.id
        output_node = node(self._func)(self._input_node, change=event_node)
        # self._fig1d.update(new_values=inspect_node.request_data(), key=inspect_node.id)
        # self._fig1d.artists[inspect_node.id].color = change['artist'].get_color()

    def update_node(self, change: Dict[str, Any]):
        event = change['event']
        n = self._event_nodes[change['artist'].nodeid]
        n.func = lambda: change
        n.notify_children(change)

    def remove_node(self, change: Dict[str, Any]):
        n = self._event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        self._fig1d.artists[pnode.id].remove()
        self._fig1d.canvas.draw()
        pnode.remove()
        n.remove()