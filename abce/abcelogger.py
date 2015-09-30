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
import pygraphviz as gv

@profile
def write_graph(nodes, edges, directory, current_round):
    network = gv.AGraph(strict=True, directed=True)
    for node, attributes in nodes:
        network.add_node(node, **attributes)

    for edge in edges:
        network.add_edge(edge)
    network.layout(prog='neato')
    #network.draw(directory +'/network%i.png' % current_round)
    network.write(directory +'/network%i.dot' % current_round)


class AbceLogger(multiprocessing.Process):
    def __init__(self, directory, in_sok):
        multiprocessing.Process.__init__(self)
        self.in_sok = in_sok
        self.directory = directory

    @profile
    def run(self):
        current_round = 0
        nodes = []
        edges = []

        while True:
            try:
                command, rnd, msg = self.in_sok.get()
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            if rnd != current_round:
                print 'in'
                #p.apply_async(write_graph,(nodes, edges, self.directory, current_round))
                write_graph(nodes, edges, self.directory, current_round)
                del nodes[:]
                del edges[:]
                current_round = rnd
                print 'out'
            if command == 'edges':
                self_name, list_of_edges = msg
                name = '%s_%i' %  self_name
                for edge in list_of_edges:
                    edges.append((name, '%s_%i' % edge))

            elif command == 'node':
                self_name, color, style, shape = msg
                nodes.append(['%s_%i' %  self_name, {'color': color, 'style': style, 'shape': shape}])

            elif command == 'close':
                print '-close'
                break

            else:
                SystemExit("command not recognized", command, rnd, msg)
        print 'out'

