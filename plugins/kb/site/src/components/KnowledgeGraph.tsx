import { useEffect, useRef, useState, useCallback } from 'react';
import {
  forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide,
} from 'd3-force';
import { zoom, zoomIdentity } from 'd3-zoom';
import { select } from 'd3-selection';
import NodeCard from './NodeCard';
import GraphControls from './GraphControls';

interface GraphNode {
  id: string;
  label: string;
  type: 'entity' | 'concept' | 'synthesis';
  dimension?: string;
  project: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  signal: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const DIMENSION_COLORS: Record<string, string> = {
  topology: '#3b82f6', api: '#10b981', 'data-model': '#f59e0b',
  flows: '#8b5cf6', concepts: '#f43f5e',
};

const TYPE_COLORS: Record<string, string> = {
  entity: '#3b82f6', concept: '#10b981', synthesis: '#f59e0b',
};

export default function KnowledgeGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<GraphData | null>(null);
  const [hoveredNode, setHoveredNode] = useState<{ node: GraphNode; x: number; y: number } | null>(null);
  const [colorMode, setColorMode] = useState<'dimension' | 'type'>('dimension');

  useEffect(() => {
    fetch('/graph.json')
      .then(r => r.json())
      .then(setData)
      .catch(() => setData({ nodes: [], edges: [] }));
  }, []);

  useEffect(() => {
    if (!data || !svgRef.current || data.nodes.length === 0) return;

    const svg = select(svgRef.current);
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    svg.selectAll('*').remove();
    const container = svg.append('g');

    const simulation = forceSimulation(data.nodes as any)
      .force('link', forceLink(data.edges).id((d: any) => d.id).distance(100))
      .force('charge', forceManyBody().strength(-200))
      .force('center', forceCenter(width / 2, height / 2))
      .force('collide', forceCollide(30));

    const zoomBehavior = zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoomBehavior);

    const getColor = (node: GraphNode) => {
      if (colorMode === 'dimension' && node.dimension) return DIMENSION_COLORS[node.dimension] || '#6b7280';
      return TYPE_COLORS[node.type] || '#6b7280';
    };

    const link = container.append('g')
      .selectAll('line')
      .data(data.edges)
      .join('line')
      .attr('stroke', 'var(--color-border)')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.6);

    const node = container.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 8)
      .attr('fill', d => getColor(d))
      .attr('cursor', 'pointer')
      .on('mouseover', (event, d) => {
        setHoveredNode({ node: d, x: event.offsetX, y: event.offsetY });
        select(event.target as Element).attr('r', 12).attr('stroke', '#fff').attr('stroke-width', 2);
      })
      .on('mouseout', (event, d) => {
        setHoveredNode(null);
        select(event.target as Element).attr('r', 8).attr('stroke', null);
      });

    const label = container.append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .text(d => d.label)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('fill', 'var(--color-text-muted)');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);
      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    return () => {
      simulation.stop();
    };
  }, [data, colorMode]);

  if (!data) return <div className="p-8 text-[var(--color-text-muted)]">加载图谱数据...</div>;
  if (data.nodes.length === 0) return <div className="p-8 text-[var(--color-text-muted)]">暂无图谱数据。运行 /kb transform 生成 wiki 页面。</div>;

  return (
    <div className="relative h-[calc(100vh-8rem)] w-full">
      <div className="absolute left-4 top-4 z-10">
        <GraphControls
          colorMode={colorMode}
          onColorModeChange={setColorMode}
          nodeCount={data.nodes.length}
          edgeCount={data.edges.length}
        />
      </div>
      <svg ref={svgRef} className="h-full w-full" />
      {hoveredNode && <NodeCard node={hoveredNode.node} x={hoveredNode.x} y={hoveredNode.y} />}
    </div>
  );
}
