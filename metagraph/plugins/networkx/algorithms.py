from metagraph import concrete_algorithm, NodeID
from metagraph.plugins import has_networkx, has_community
from typing import Tuple, Iterable, Any


if has_networkx:
    import networkx as nx
    import numpy as np
    from .types import NetworkXEdgeSet, NetworkXEdgeMap
    from ..python.types import PythonNodeMap, PythonNodeSet
    from ..numpy.types import NumpyVector

    @concrete_algorithm("link_analysis.pagerank")
    def nx_pagerank(
        graph: NetworkXEdgeMap, damping: float, maxiter: int, tolerance: float
    ) -> PythonNodeMap:
        pagerank = nx.pagerank(
            graph.value, alpha=damping, max_iter=maxiter, tol=tolerance, weight=None
        )
        return PythonNodeMap(pagerank)

    @concrete_algorithm("link_analysis.katz_centrality")
    def nx_katz_centrality(
        graph: NetworkXEdgeMap,
        attenuation_factor: float,
        immediate_neighbor_weight: float,
        maxiter: int,
        tolerance: float,
    ) -> PythonNodeMap:
        katz_centrality_scores = nx.katz_centrality(
            graph.value,
            alpha=attenuation_factor,
            beta=immediate_neighbor_weight,
            max_iter=maxiter,
            tol=tolerance,
            weight=graph.weight_label,
        )
        return PythonNodeMap(katz_centrality_scores)

    @concrete_algorithm("cluster.triangle_count")
    def nx_triangle_count(graph: NetworkXEdgeSet) -> int:
        triangles = nx.triangles(graph.value)
        # Sum up triangles from each node
        # Divide by 3 because each triangle is counted 3 times
        total_triangles = sum(triangles.values()) // 3
        return total_triangles

    @concrete_algorithm("clustering.connected_components")
    def nx_connected_components(graph: NetworkXEdgeSet) -> PythonNodeMap:
        index_to_label = dict()
        for i, nodes in enumerate(nx.connected_components(graph.value)):
            for node in nodes:
                index_to_label[node] = i
        return PythonNodeMap(index_to_label,)

    @concrete_algorithm("clustering.strongly_connected_components")
    def nx_strongly_connected_components(graph: NetworkXEdgeSet) -> PythonNodeMap:
        index_to_label = dict()
        for i, nodes in enumerate(nx.strongly_connected_components(graph.value)):
            for node in nodes:
                index_to_label[node] = i
        return PythonNodeMap(index_to_label,)

    @concrete_algorithm("clustering.label_propagation_community")
    def nx_label_propagation_community(graph: NetworkXEdgeMap) -> PythonNodeMap:
        communities = nx.algorithms.community.label_propagation.label_propagation_communities(
            graph.value
        )
        index_to_label = dict()
        for label, nodes in enumerate(communities):
            for node in nodes:
                index_to_label[node] = label
        return PythonNodeMap(index_to_label,)

    @concrete_algorithm("subgraph.extract_edgemap")
    def nx_extract_edgemap(
        graph: NetworkXEdgeMap, nodes: PythonNodeSet
    ) -> NetworkXEdgeMap:
        subgraph = graph.value.subgraph(nodes.value)
        return NetworkXEdgeMap(subgraph, weight_label=graph.weight_label,)

    @concrete_algorithm("subgraph.extract_edgeset")
    def nx_extract_edgeset(
        graph: NetworkXEdgeSet, nodes: PythonNodeSet
    ) -> NetworkXEdgeSet:
        subgraph = graph.value.subgraph(nodes.value)
        return NetworkXEdgeSet(subgraph)

    @concrete_algorithm("subgraph.k_core")
    def nx_k_core(graph: NetworkXEdgeMap, k: int) -> NetworkXEdgeMap:
        k_core_graph = nx.k_core(graph.value, k)
        return NetworkXEdgeMap(k_core_graph, weight_label=graph.weight_label,)

    @concrete_algorithm("subgraph.k_core_unweighted")
    def nx_k_core_unweighted(graph: NetworkXEdgeSet, k: int) -> NetworkXEdgeSet:
        k_core_graph = nx.k_core(graph.value, k)
        return NetworkXEdgeSet(k_core_graph)

    @concrete_algorithm("traversal.bellman_ford")
    def nx_bellman_ford(
        graph: NetworkXEdgeMap, source_node: NodeID
    ) -> Tuple[PythonNodeMap, PythonNodeMap]:
        predecessors_map, distance_map = nx.bellman_ford_predecessor_and_distance(
            graph.value, source_node
        )
        single_parent_map = {
            child: parents[0] if len(parents) > 0 else source_node
            for child, parents in predecessors_map.items()
        }
        return (
            PythonNodeMap(single_parent_map,),
            PythonNodeMap(distance_map,),
        )

    @concrete_algorithm("traversal.dijkstra")
    def dijkstra(
        graph: NetworkXEdgeMap, source_node: NodeID, max_path_length: float
    ) -> Tuple[PythonNodeMap, PythonNodeMap]:
        predecessors_map, distance_map = nx.dijkstra_predecessor_and_distance(
            graph.value, source_node, cutoff=max_path_length,
        )
        single_parent_map = {
            child: parents[0] if len(parents) > 0 else source_node
            for child, parents in predecessors_map.items()
        }
        return (
            PythonNodeMap(single_parent_map,),
            PythonNodeMap(distance_map,),
        )

    @concrete_algorithm("vertex_ranking.betweenness_centrality")
    def nx_betweenness_centrality(
        graph: NetworkXEdgeMap,
        k: int,
        enable_normalization: bool,
        include_endpoints: bool,
    ) -> PythonNodeMap:
        node_to_score_map = nx.betweenness_centrality(
            graph.value, k, enable_normalization, include_endpoints
        )
        return PythonNodeMap(node_to_score_map,)

    @concrete_algorithm("traversal.breadth_first_search")
    def nx_breadth_first_search(
        graph: NetworkXEdgeSet, source_node: NodeID
    ) -> NumpyVector:
        bfs_ordered_node_array = np.array(
            nx.breadth_first_search.bfs_tree(graph.value, source_node)
        )
        return NumpyVector(bfs_ordered_node_array)


if has_community:
    import community as community_louvain
    from .types import NetworkXEdgeMap
    from ..python.types import PythonNodeMap

    @concrete_algorithm("clustering.louvain_community")
    def nx_louvain_community(graph: NetworkXEdgeMap) -> Tuple[PythonNodeMap, float]:
        index_to_label = community_louvain.best_partition(graph.value)
        modularity_score = community_louvain.modularity(index_to_label, graph.value)
        return (
            PythonNodeMap(index_to_label,),
            modularity_score,
        )
