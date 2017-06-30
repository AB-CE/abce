# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
import multiprocessing
import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
except RuntimeError:
    pass


class AbceLogger(multiprocessing.Process):
    def __init__(self, directory, in_sok, savefig, savegml, figsize, dpi, pos_fixed, alpha):
        multiprocessing.Process.__init__(self)
        self.in_sok = in_sok
        self.directory = directory
        self.savefig = savefig
        self.savegml = savegml
        self.figsize = figsize
        self.dpi = dpi
        self.pos_fixed = pos_fixed
        self.alpha = alpha

    def run(self):
        current_round = 0
        nodes = []
        edges = []
        colors = {}
        self.pos = None

        while True:
            try:
                command, rnd, msg = self.in_sok.get()
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            if rnd != current_round:
                self._write_graph(nodes, edges, colors, current_round)
                del nodes[:]
                del edges[:]
                colors.clear()
                current_round = rnd

            if command == 'edges':
                self_name, list_of_edges = msg
                name = '%s %i' % self_name
                for edge in list_of_edges:
                    edges.append((name, '%s %i' % edge))

            elif command == 'node':
                self_name, color, style, shape = msg
                name = '%s %i' % self_name
                nodes.append(
                    [name, {'label': name, 'color': color, 'shape': shape}])
                colors[name] = color

            elif command == 'close':
                break

            else:
                Exception("command not recognized", command, rnd, msg)

    def _write_graph(self, nodes, edges, colors, current_round):
        network = nx.Graph(strict=True, directed=True)
        for node, attributes in nodes:
            network.add_node(node, shape=attributes['shape'])

        for edge in edges:
            network.add_edge(edge[0], edge[1])

        if self.savegml:
            nx.write_gml(network, self.directory +
                         '/network%05d.gml' % current_round)

        if self.savefig:
            try:
                if self.pos is None or not self.pos_fixed:
                    # positions for all nodes
                    self.pos = nx.spring_layout(network, pos=self.pos)
                plt.figure(1, figsize=self.figsize)
                nodeShapes = set((aShape[1]["shape"]
                                  for aShape in network.nodes(data=True)))
                for aShape in nodeShapes:
                    nodelist = [sNode[0]
                                for sNode in [x for x in network.nodes(data=True) if x[1]["shape"] == aShape]]
                    nx.draw_networkx_nodes(network,
                                           self.pos,
                                           node_shape=aShape,
                                           nodelist=nodelist,
                                           node_color=[colors[node]
                                                       for node in nodelist],
                                           alpha=self.alpha)
                nx.draw_networkx_edges(network, self.pos)
                plt.savefig(self.directory + '/network%05d.png' %
                            current_round, dpi=self.dpi)
                plt.close()
            except NameError:
                raise NameError(
                    "matplotlib not installed: sudo apt-get install matplotlib; or pip install matplotlib")
