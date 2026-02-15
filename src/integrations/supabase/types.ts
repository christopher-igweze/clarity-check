export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  public: {
    Tables: {
      action_items: {
        Row: {
          category: string
          created_at: string
          cto_perspective: string | null
          description: string | null
          file_path: string | null
          fix_status: string
          id: string
          line_number: number | null
          project_id: string
          scan_report_id: string
          severity: string
          source: string
          title: string
          user_id: string
          why_it_matters: string | null
        }
        Insert: {
          category: string
          created_at?: string
          cto_perspective?: string | null
          description?: string | null
          file_path?: string | null
          fix_status?: string
          id?: string
          line_number?: number | null
          project_id: string
          scan_report_id: string
          severity: string
          source?: string
          title: string
          user_id: string
          why_it_matters?: string | null
        }
        Update: {
          category?: string
          created_at?: string
          cto_perspective?: string | null
          description?: string | null
          file_path?: string | null
          fix_status?: string
          id?: string
          line_number?: number | null
          project_id?: string
          scan_report_id?: string
          severity?: string
          source?: string
          title?: string
          user_id?: string
          why_it_matters?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "action_items_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "action_items_scan_report_id_fkey"
            columns: ["scan_report_id"]
            isOneToOne: false
            referencedRelation: "scan_reports"
            referencedColumns: ["id"]
          },
        ]
      }
      fix_attempts: {
        Row: {
          action_item_id: string
          agent_logs: Json | null
          completed_at: string | null
          created_at: string
          diff_preview: string | null
          id: string
          pr_url: string | null
          project_id: string
          sandbox_id: string | null
          started_at: string | null
          status: string
          user_id: string
        }
        Insert: {
          action_item_id: string
          agent_logs?: Json | null
          completed_at?: string | null
          created_at?: string
          diff_preview?: string | null
          id?: string
          pr_url?: string | null
          project_id: string
          sandbox_id?: string | null
          started_at?: string | null
          status?: string
          user_id: string
        }
        Update: {
          action_item_id?: string
          agent_logs?: Json | null
          completed_at?: string | null
          created_at?: string
          diff_preview?: string | null
          id?: string
          pr_url?: string | null
          project_id?: string
          sandbox_id?: string | null
          started_at?: string | null
          status?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "fix_attempts_action_item_id_fkey"
            columns: ["action_item_id"]
            isOneToOne: false
            referencedRelation: "action_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fix_attempts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string
          display_name: string | null
          github_username: string | null
          id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          display_name?: string | null
          github_username?: string | null
          id?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          display_name?: string | null
          github_username?: string | null
          id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      projects: {
        Row: {
          created_at: string
          id: string
          latest_health_score: number | null
          latest_scan_tier: string | null
          project_charter: Json | null
          repo_name: string | null
          repo_url: string
          scan_count: number
          updated_at: string
          user_id: string
          vibe_prompt: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          latest_health_score?: number | null
          latest_scan_tier?: string | null
          project_charter?: Json | null
          repo_name?: string | null
          repo_url: string
          scan_count?: number
          updated_at?: string
          user_id: string
          vibe_prompt?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          latest_health_score?: number | null
          latest_scan_tier?: string | null
          project_charter?: Json | null
          repo_name?: string | null
          repo_url?: string
          scan_count?: number
          updated_at?: string
          user_id?: string
          vibe_prompt?: string | null
        }
        Relationships: []
      }
      scan_reports: {
        Row: {
          agent_logs: Json | null
          completed_at: string | null
          created_at: string
          health_score: number | null
          id: string
          project_id: string
          reliability_score: number | null
          report_data: Json | null
          scalability_score: number | null
          scan_tier: string
          security_review: Json | null
          security_score: number | null
          started_at: string | null
          status: string
          user_id: string
        }
        Insert: {
          agent_logs?: Json | null
          completed_at?: string | null
          created_at?: string
          health_score?: number | null
          id?: string
          project_id: string
          reliability_score?: number | null
          report_data?: Json | null
          scalability_score?: number | null
          scan_tier: string
          security_review?: Json | null
          security_score?: number | null
          started_at?: string | null
          status?: string
          user_id: string
        }
        Update: {
          agent_logs?: Json | null
          completed_at?: string | null
          created_at?: string
          health_score?: number | null
          id?: string
          project_id?: string
          reliability_score?: number | null
          report_data?: Json | null
          scalability_score?: number | null
          scan_tier?: string
          security_review?: Json | null
          security_score?: number | null
          started_at?: string | null
          status?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "scan_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      trajectories: {
        Row: {
          code_changes: Json | null
          created_at: string
          fix_attempt_id: string
          id: string
          project_id: string
          prompt: string | null
          success: boolean
          test_results: Json | null
          user_id: string
        }
        Insert: {
          code_changes?: Json | null
          created_at?: string
          fix_attempt_id: string
          id?: string
          project_id: string
          prompt?: string | null
          success?: boolean
          test_results?: Json | null
          user_id: string
        }
        Update: {
          code_changes?: Json | null
          created_at?: string
          fix_attempt_id?: string
          id?: string
          project_id?: string
          prompt?: string | null
          success?: boolean
          test_results?: Json | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "trajectories_fix_attempt_id_fkey"
            columns: ["fix_attempt_id"]
            isOneToOne: false
            referencedRelation: "fix_attempts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "trajectories_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
