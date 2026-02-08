/**
 * MCP style variables for the basic-host example.
 * These are passed to apps via hostContext.styles.variables.
 */
import type { McpUiStyles } from "@modelcontextprotocol/ext-apps";

/**
 * MCP App style variables using light-dark() for theme adaptation.
 * Apps receive these and can use them as CSS custom properties.
 */
export const HOST_STYLE_VARIABLES: McpUiStyles = {
  // Background colors - Blueprint adaptation
  "--color-background-primary": "var(--bg-color)",
  "--color-background-secondary": "var(--card-bg)",
  "--color-background-tertiary": "rgba(0, 85, 170, 0.5)",
  "--color-background-inverse": "#ffffff",
  "--color-background-ghost": "transparent",
  "--color-background-info": "rgba(30, 58, 138, 0.5)",
  "--color-background-danger": "rgba(127, 29, 29, 0.5)",
  "--color-background-success": "rgba(20, 83, 45, 0.5)",
  "--color-background-warning": "rgba(113, 63, 18, 0.5)",
  "--color-background-disabled": "rgba(255, 255, 255, 0.1)",

  // Text colors
  "--color-text-primary": "#ffffff",
  "--color-text-secondary": "rgba(255, 255, 255, 0.8)",
  "--color-text-tertiary": "rgba(255, 255, 255, 0.6)",
  "--color-text-inverse": "#0055aa",
  "--color-text-ghost": "rgba(255, 255, 255, 0.4)",
  "--color-text-info": "#60a5fa",
  "--color-text-danger": "#f87171",
  "--color-text-success": "#4ade80",
  "--color-text-warning": "#fbbf24",
  "--color-text-disabled": "rgba(255, 255, 255, 0.3)",

  // Border colors
  "--color-border-primary": "#ffffff",
  "--color-border-secondary": "rgba(255, 255, 255, 0.7)",
  "--color-border-tertiary": "rgba(255, 255, 255, 0.5)",
  "--color-border-inverse": "rgba(0, 0, 0, 0.3)",
  "--color-border-ghost": "transparent",
  "--color-border-info": "#3b82f6",
  "--color-border-danger": "#ef4444",
  "--color-border-success": "#22c55e",
  "--color-border-warning": "#eab308",
  "--color-border-disabled": "rgba(255, 255, 255, 0.2)",

  // Ring colors (focus)
  "--color-ring-primary": "#ffffff",
  "--color-ring-secondary": "rgba(255, 255, 255, 0.5)",
  "--color-ring-inverse": "#0055aa",
  "--color-ring-info": "#3b82f6",
  "--color-ring-danger": "#ef4444",
  "--color-ring-success": "#22c55e",
  "--color-ring-warning": "#eab308",

  // Typography - Family
  "--font-sans": "'Rajdhani', sans-serif",
  "--font-mono": "ui-monospace, 'SF Mono', Monaco, 'Cascadia Code', monospace",

  // Typography - Weight
  "--font-weight-normal": "500",
  "--font-weight-medium": "600",
  "--font-weight-semibold": "700",
  "--font-weight-bold": "700",

  // Typography - Text Size
  "--font-text-xs-size": "0.75rem",
  "--font-text-sm-size": "0.875rem",
  "--font-text-md-size": "1rem",
  "--font-text-lg-size": "1.125rem",

  // Typography - Heading Size
  "--font-heading-xs-size": "0.875rem",
  "--font-heading-sm-size": "1rem",
  "--font-heading-md-size": "1.25rem",
  "--font-heading-lg-size": "1.5rem",
  "--font-heading-xl-size": "1.875rem",
  "--font-heading-2xl-size": "2.25rem",
  "--font-heading-3xl-size": "3rem",

  // Typography - Text Line Height
  "--font-text-xs-line-height": "1.4",
  "--font-text-sm-line-height": "1.4",
  "--font-text-md-line-height": "1.5",
  "--font-text-lg-line-height": "1.5",

  // Typography - Heading Line Height
  "--font-heading-xs-line-height": "1.2",
  "--font-heading-sm-line-height": "1.2",
  "--font-heading-md-line-height": "1.2",
  "--font-heading-lg-line-height": "1.1",
  "--font-heading-xl-line-height": "1.1",
  "--font-heading-2xl-line-height": "1",
  "--font-heading-3xl-line-height": "1",

  // Border radius -> Technical/Sharp look
  "--border-radius-xs": "0px",
  "--border-radius-sm": "0px",
  "--border-radius-md": "0px",
  "--border-radius-lg": "0px",
  "--border-radius-xl": "0px",
  "--border-radius-full": "9999px", // Keep round for badges/pills if needed

  // Border width
  "--border-width-regular": "1px",

  // Shadows
  "--shadow-hairline": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
  "--shadow-sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
  "--shadow-md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
  "--shadow-lg": "0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.2)",
};
