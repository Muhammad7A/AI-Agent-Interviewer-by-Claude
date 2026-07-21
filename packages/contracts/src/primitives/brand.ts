/**
 * Compile-time nominal ("branded") typing.
 *
 * The domain uses many identifiers and scalars that are structurally identical
 * (all `string` or `number`) yet must never be interchangeable — a
 * `TenantId` is not an `EngagementId`. Branding gives each a distinct
 * compile-time identity while remaining a plain primitive at runtime: the brand
 * marker is ambient and emits no JavaScript.
 *
 * Contracts only — this module has no runtime footprint.
 */
declare const brand: unique symbol;

/** A `TBase` primitive tagged with a unique compile-time brand `TBrand`. */
export type Brand<TBase, TBrand extends string> = TBase & {
  readonly [brand]: TBrand;
};
