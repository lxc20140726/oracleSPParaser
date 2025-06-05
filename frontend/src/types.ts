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
  computed_fields?: ComputedField[];
  source_sql_ids: string[];
}

export interface ComputedField {
  name: string;
  expression: string;
  source_fields: string[];
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
  uml_visualization?: UMLVisualizationData;
}

export interface UMLVisualizationData {
  visualization_type: "uml";
  nodes: UMLNode[];
  field_mappings: UMLEdge[];
  table_relations: UMLEdge[];
  metadata: {
    procedure_name: string;
    total_tables: number;
    field_mappings_count: number;
    table_relations_count: number;
    physical_tables: number;
    temp_tables: number;
  };
}

export interface UMLNode {
  id: string;
  label: string;
  type: string;
  properties: UMLNodeProperties;
}

export interface UMLNodeProperties {
  table_name: string;
  fields: UMLField[];
  field_count: number;
  color: string;
  border_style: string;
  is_temporary: boolean;
  shape: string;
  width: number;
  height: number;
  field_layout?: {
    header_height: number;
    field_height: number;
    padding: number;
  };
  sql_ids?: string[];
  selected_field?: {
    name: string;
    type: string;
    index: number;
    is_computed: boolean;
    expression?: string;
  };
}

export interface UMLField {
  name: string;
  type: "field" | "computed_field";
  source?: string;
  expression?: string;
  source_fields?: string[];
}

export interface UMLEdge {
  source: string;
  target: string;
  label: string;
  type: string;
  properties: {
    id?: string;
    source_table?: string;
    source_field?: string;
    target_table?: string;
    target_field?: string;
    mapping_type?: string;
    expression?: string;
    relation_type?: string;
    left_field?: string;
    right_field?: string;
    condition?: string;
    style: string;
    color: string;
    source_field_index?: number;
    target_field_index?: number;
    connection_style?: string;
    width?: string;
    arrow_type?: string;
  };
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