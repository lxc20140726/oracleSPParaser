export interface Parameter {
  name: string;
  direction: 'IN' | 'OUT' | 'INOUT';
  data_type: string;
  used_in_statements: string[];
}

export interface SqlStatement {
  id: string;
  type: string;
  raw_sql: string;
  source_tables: string[];
  target_tables: string[];
  parameters_used: string[];
}

export interface Table {
  fields: string[];
  source_sql_ids: string[];
}

export interface JoinCondition {
  left_table: string;
  left_field: string;
  right_table: string;
  right_field: string;
  join_type: string;
  condition_text: string;
}

export interface Statistics {
  parameter_count: number;
  sql_statement_count: number;
  physical_table_count: number;
  temporary_table_count: number;
  join_condition_count: number;
}

export interface AnalysisData {
  procedure_name: string;
  parameters: Parameter[];
  sql_statements: SqlStatement[];
  tables: {
    physical: Record<string, Table>;
    temporary: Record<string, Table>;
  };
  join_conditions: JoinCondition[];
  statistics: Statistics;
}

export interface VisualizationNode {
  id: string;
  label: string;
  type: string;
  group: string;
  data: Record<string, any>;
}

export interface VisualizationEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  data: Record<string, any>;
}

export interface VisualizationData {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  layout: string;
  metadata: {
    node_count: number;
    edge_count: number;
    generated_at: string;
  };
}

export interface AnalysisResult {
  success: boolean;
  message: string;
  data: AnalysisData;
  visualization: VisualizationData;
}

export interface AnalyzeRequest {
  stored_procedure: string;
  options?: Record<string, any>;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
} 