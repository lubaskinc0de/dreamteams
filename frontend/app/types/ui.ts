/**
 * UI-related type definitions for components and pages
 * Ensures type safety for UI data structures
 */

/**
 * Feature card for landing page
 */
export interface Feature {
  icon: string;
  title: string;
  description: string;
  badge: {
    label: string;
    color:
      | "success"
      | "info"
      | "warning"
      | "error"
      | "primary"
      | "secondary"
      | "neutral";
  };
}

/**
 * Statistics display item
 */
export interface Stat {
  icon: string;
  value: string;
  label: string;
  color: string;
}

/**
 * Navigation link
 */
export interface NavLink {
  label: string;
  icon: string;
  to: string;
}

/**
 * Hero action button
 */
export interface HeroLink {
  label: string;
  icon: string;
  size: "xs" | "sm" | "md" | "lg" | "xl";
  variant?: "solid" | "outline" | "soft" | "ghost" | "link";
  color?:
    | "primary"
    | "secondary"
    | "success"
    | "info"
    | "warning"
    | "error"
    | "neutral";
  click: () => void;
}

/**
 * Available theme names
 */
export type ThemeName = "default" | "ocean" | "forest" | "sunset";

/**
 * Theme configuration
 */
export interface ThemeConfig {
  primary: string;
  gray: string;
}

/**
 * Available color modes
 */
export type ColorMode = "light" | "dark" | "system";

/**
 * Toast notification type
 */
export interface ToastNotification {
  title: string;
  description?: string;
  icon?: string;
  color?:
    | "primary"
    | "secondary"
    | "success"
    | "info"
    | "warning"
    | "error"
    | "neutral";
  duration?: number;
}

/**
 * Form field state
 */
export interface FormFieldState {
  value: string;
  error: string | null;
  touched: boolean;
  dirty: boolean;
}

/**
 * Skeleton loader configuration
 */
export interface SkeletonConfig {
  height: string;
  width: string;
  rounded?: string;
  className?: string;
}

/**
 * Testimonial for landing page
 */
export interface Testimonial {
  name: string;
  role: string;
  avatar: string;
  text: string;
}
