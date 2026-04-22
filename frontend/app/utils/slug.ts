/**
 * Generate a machine-readable identifier from a human label.
 * - Lowercases, trims.
 * - Replaces runs of non-letter/non-digit characters with `_`.
 * - Strips leading/trailing `_`.
 * - Falls back to `fallback` when the result would be empty.
 */
export const slugify = (input: string, fallback = "field"): string => {
  const slug = input
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "_")
    .replace(/^_+|_+$/g, "");
  return slug.length > 0 ? slug : fallback;
};

/**
 * Assign unique machine names to an ordered list of labels by slugging each
 * label and appending `_2`, `_3`, … when a slug is already taken.
 */
export const uniqueSlugs = (labels: string[]): string[] => {
  const seen = new Map<string, number>();
  return labels.map((label, i) => {
    const base = slugify(label, `field_${i + 1}`);
    const count = (seen.get(base) ?? 0) + 1;
    seen.set(base, count);
    return count === 1 ? base : `${base}_${count}`;
  });
};
