# Frontend conventions — Next.js, Pages Router

Default frontend. Applies to **new** code; on existing projects, conform to what's there per
precedence (`references/memory.md`).

## Stack

- **Next.js** with the **Pages Router** (not App Router — this is a deliberate project choice).
- **TypeScript**, strict.
- **pnpm**.
- **Tailwind CSS** for styling.
- **shadcn/ui** for components. Note: shadcn docs lean App Router — adapt examples to Pages
  Router (no server components; data fetching is `getServerSideProps`/`getStaticProps` + the
  client query layer).
- **TanStack Query** for all server state (fetching + caching).
- **Zustand** for client/UI state.
- **react-hook-form + Zod** for forms and validation.

Verify current idioms with web search before building — these libraries move, and Pages-Router
guidance is increasingly buried under App-Router content.

## Pages Router data pattern

This is the standard, since it's the most surprising part of the choice:

- **Server-side data on first load** via `getServerSideProps` (per-request) or
  `getStaticProps` (build-time / ISR) — choose based on whether data is request-specific.
- **Client-side data and mutations** via **TanStack Query** — it owns the cache, loading, and
  refetch. Don't hand-roll `useEffect` + `fetch`; that recreates caching badly and duplicates
  loading/error handling across components.
- A typed **API client module** wraps calls to the FastAPI backend in one place. Components
  never embed raw URLs or fetch logic.

## Layout

```
frontend/
  src/
    pages/             routes (Pages Router); _app.tsx wires providers
    components/
      ui/              shadcn primitives
      <feature>/       feature-specific composed components
    features/          feature modules (hooks, queries, types per feature)
    lib/
      api/             typed API client (one place that talks to the backend)
      query/           TanStack Query client + keys
    stores/            Zustand stores
    styles/
  package.json
```

## Componentisation & DRY rules

- **Three repetitions → extract.** Copy a block of JSX or logic a third time and it becomes a
  component or a hook. Don't pre-abstract on the first use; do extract by the third.
- **Presentational vs. container split.** Components that render are dumb (props in, markup
  out). Data fetching lives in hooks (`useXQuery`) or `getServerSideProps`, not inside the
  presentational component. This keeps components reusable and testable.
- **Query keys are centralised** in `lib/query` so cache invalidation is consistent and not
  guessed per-call-site.
- **Forms: schema first.** Define the Zod schema once; derive the TS type from it and feed it
  to react-hook-form. One source of truth for shape and validation.
- **No prop drilling past two levels.** Beyond that, a Zustand store or a query hook. Don't
  thread props through intermediaries that don't use them.
- **Tailwind, not bespoke CSS files**, unless the project already does otherwise. Extract
  repeated class strings into components, not into `@apply` soup.

## Reading existing frontend code

Name the hidden assumption before trusting it: is this component re-rendering because state
genuinely changed, or because a new object identity is created each render? Is this data
actually loaded when the component mounts, or assumed loaded? Flag it.
